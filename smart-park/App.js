import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, SafeAreaView, Alert, ActivityIndicator } from 'react-native';
import axios from 'axios';
import MapView, { Marker } from 'react-native-maps';
import * as Location from 'expo-location';

export default function App() {
  const [cameraData, setCameraData] = useState({});
  const [currentLocation, setCurrentLocation] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchParkingData = async () => {
      try {
        const response = await axios.get('http://51.20.185.217:4000/api/parking-data');
        const formattedData = response.data.reduce((acc, camera) => {
          acc[camera.camera_id] = camera;
          return acc;
        }, {});
        setCameraData(formattedData);
      } catch (error) {
        console.error('Error fetching parking data:', error);
        Alert.alert('Error', 'Unable to fetch parking data. Please try again later.');
      }
    };

    const getLocation = async () => {
      try {
        const { status } = await Location.requestForegroundPermissionsAsync();
        if (status !== 'granted') {
          Alert.alert('Permission Denied', 'Location permission is required to show your current location.');
          return;
        }

        const location = await Location.getCurrentPositionAsync({});
        setCurrentLocation(location.coords);
      } catch (error) {
        console.error('Error fetching location:', error);
        Alert.alert('Error', 'Unable to fetch your location. Please check your device settings.');
      } finally {
        setLoading(false);
      }
    };

    fetchParkingData();
    getLocation();

    const interval = setInterval(fetchParkingData, 1000);

    return () => clearInterval(interval);
  }, []);

  const generateCustomMarker = (freeSpaces) => (
    <View
      style={[
        styles.markerContainer,
        { backgroundColor: freeSpaces > 0 ? '#4CAF50' : '#FF5722' },
      ]}
    >
      <Text style={styles.markerText}>{freeSpaces}</Text>
    </View>
  );

  if (loading) {
    return (
      <SafeAreaView style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#6200EE" />
        <Text style={styles.loadingText}>Fetching current location...</Text>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      {currentLocation ? (
        <MapView
          style={styles.map}
          initialRegion={{
            latitude: currentLocation.latitude,
            longitude: currentLocation.longitude,
            latitudeDelta: 0.05,
            longitudeDelta: 0.05,
          }}
          showsUserLocation={true}
        >
          {Object.keys(cameraData).map((cameraKey) => (
            <Marker
              key={cameraKey}
              coordinate={{
                latitude: cameraData[cameraKey].latitude || 0,
                longitude: cameraData[cameraKey].longitude || 0,
              }}
              title={cameraKey}
              description={`Free Spaces: ${cameraData[cameraKey].free_spaces}, Total Spaces: ${cameraData[cameraKey].total_spaces}`}
            >
              {generateCustomMarker(cameraData[cameraKey].free_spaces)}
            </Marker>
          ))}
        </MapView>
      ) : (
        <View style={styles.loadingContainer}>
          <Text style={styles.loadingText}>Fetching current location...</Text>
        </View>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'flex-start',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
  },
  map: {
    width: '100%',
    height: '100%',
    marginTop: 5,
  },
  markerContainer: {
    justifyContent: 'center',
    alignItems: 'center',
    width: 30,
    height: 30,
    borderRadius: 25,
    borderWidth: 2,
    borderColor: 'white',
  },
  markerText: {
    fontSize: 14,
    color: 'white',
    fontWeight: 'bold',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    fontSize: 18,
    color: '#555',
  },
});
