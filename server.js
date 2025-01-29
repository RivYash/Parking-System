const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');

const app = express();
const port = 4000;

// Enable CORS for React Native to access the API
app.use(cors());
app.use(express.json());

// MongoDB connection string (use your actual credentials and database name)
const mongoURI = "mongodb+srv://mongo:GqJDx8ymHaFGUcOM@cluster0.4icd0.mongodb.net/parking_system?retryWrites=true&w=majority"; // Added the database name `parking_system`

mongoose.connect(mongoURI) // Removed deprecated options
  .then(() => console.log('MongoDB connected'))
  .catch((err) => console.log(err));

// Schema for parking data
const parkingSchema = new mongoose.Schema({
  camera_id: String, // camera1 or camera2
  free_spaces: Number,
  latitude: Number,
  longitude: Number,
  total_spaces: Number
});

// Define the Parking model to interact with the `parking_data` collection
const Parking = mongoose.model('Parking', parkingSchema, 'parking_data');

// API endpoint to fetch parking data
app.get('/api/parking-data', async (req, res) => {
  try {
    // Fetch all documents from the parking_data collection
    const data = await Parking.find(); // Find all documents instead of just one
    res.json(data); // Return the data as JSON
  } catch (err) {
    res.status(500).send('Error fetching data');
  }
});

app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});
