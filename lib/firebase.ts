import { initializeApp, getApps, getApp } from "firebase/app";
import { getDatabase } from "firebase/database";

const firebaseConfig = {
  apiKey: "AIzaSyB5wgzflTU5528apaBcHs3cHnLtzqhId-Y",
  authDomain: "skripsigoat.firebaseapp.com",
  databaseURL: "https://skripsigoat-default-rtdb.asia-southeast1.firebasedatabase.app", 
  projectId: "skripsigoat",
  storageBucket: "skripsigoat.firebasestorage.app",
  messagingSenderId: "1032248376260",
  appId: "1:1032248376260:web:fa49851b505e98041a8291",
  measurementId: "G-5EQYJT7YWG"
};

// Initialize Firebase only if it hasn't been initialized already
const app = !getApps().length ? initializeApp(firebaseConfig) : getApp();

// Get the Realtime Database instance
const database = getDatabase(app);

export { app, database };
