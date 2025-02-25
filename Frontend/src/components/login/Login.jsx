import React, { useEffect, useState } from "react";
import { useGoogleLogin } from "@react-oauth/google";
import axios from "axios";

const Login = ({ setUser }) => {
  const [user, setUserState] = useState(null);
  const [latitude, setLatitude] = useState("");
  const [longitude, setLongitude] = useState("");

  useEffect(() => {
    // Load user from localStorage on page load
    const savedUser = localStorage.getItem("user");
    if (savedUser) {
      const parsedUser = JSON.parse(savedUser);
      setUserState(parsedUser);
      setUser(parsedUser);
      setLatitude(parsedUser.latitude || ""); // Load saved latitude
      setLongitude(parsedUser.longitude || ""); // Load saved longitude
    }
  }, [setUser]);

  const login = useGoogleLogin({
    onSuccess: async (tokenResponse) => {
      try {
        // Fetch user data from Google
        const response = await axios.get("https://www.googleapis.com/oauth2/v3/userinfo", {
          headers: { Authorization: `Bearer ${tokenResponse.access_token}` },
        });

        const userData = response.data;

        // Get user location automatically
        const location = await getLocation();

        // Send login data to backend
        const backendResponse = await axios.post("http://localhost:5000/api/google-login", {
          email: userData.email,
          name: userData.name,
          profile_picture: userData.picture,
          latitude: location.latitude,
          longitude: location.longitude,
        });

        if (backendResponse.data.userId) {
          const fullUserData = {
            ...userData,
            userId: backendResponse.data.userId,
            latitude: location.latitude,
            longitude: location.longitude,
          };

          // Save user in state & localStorage
          setUserState(fullUserData);
          setUser(fullUserData);
          localStorage.setItem("user", JSON.stringify(fullUserData));

          // Set location in input fields
          setLatitude(location.latitude);
          setLongitude(location.longitude);
        }
      } catch (error) {
        console.error("Login Error:", error);
      }
    },
    onError: (error) => console.log("Login Failed:", error),
  });

  const getLocation = () => {
    return new Promise((resolve, reject) => {
      navigator.geolocation.getCurrentPosition(
        (position) => resolve({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
        }),
        (error) => reject(error)
      );
    });
  };

  const updateLocation = async () => {
    if (!latitude || !longitude || !user || !user.userId) {
      alert("Please enter valid latitude and longitude.");
      return;
    }

    try {
      const response = await axios.post("http://localhost:5000/api/update-location", {
        userId: user.userId,
        latitude,
        longitude,
      });

      if (response.data.success) {
        const updatedUser = { ...user, latitude, longitude };
        setUserState(updatedUser);
        setUser(updatedUser);
        localStorage.setItem("user", JSON.stringify(updatedUser));
        alert("Location updated successfully!");
      } else {
        console.error("Failed to update location:", response.data.error);
      }
    } catch (error) {
      console.error("Error updating location:", error);
    }
  };

  const logout = () => {
    localStorage.removeItem("user");
    setUserState(null);
    setUser(null);
  };

  return (
    <div style={{ textAlign: "center", marginTop: "50px" }}>
      <h2>Login Page</h2>
      {user ? (
        <div>
          <p>Welcome, {user.name}!</p>
          <img src={user.picture} alt="Profile" width="100" />
          <p>Location: {user.latitude}, {user.longitude}</p>
          
          {/* Manual Location Input */}
          <div>
            <label>Latitude:</label>
            <input 
              type="text" 
              value={latitude} 
              onChange={(e) => setLatitude(e.target.value)} 
              placeholder="Enter latitude" 
            />
            <br />
            <label>Longitude:</label>
            <input 
              type="text" 
              value={longitude} 
              onChange={(e) => setLongitude(e.target.value)} 
              placeholder="Enter longitude" 
            />
            <br />
            <button onClick={updateLocation}>Update Location</button>
          </div>

          <br />
          <button onClick={logout}>Logout</button>
        </div>
      ) : (
        <button onClick={() => login()}>Login with Google</button>
      )}
    </div>
  );
};

export default Login;
