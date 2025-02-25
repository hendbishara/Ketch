import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom"; // Redirect users to login if not logged in
import "./requestOrder.css";

const storeMapping = {
  "AllModern": 1,
  "Room&Board": 2,
  "West Elm": 3,
  "Living Spaces": 4,
};

const RequestOrder = () => {
  const [userId, setUserId] = useState(null); // Store user ID dynamically
  const [store, setStore] = useState("");
  const [items, setItems] = useState([{ itemNumber: "", quantity: 1 }]);
  const [timeToWait, setTimeToWait] = useState("");
  const [notes, setNotes] = useState("");
  const [errorItems, setErrorItems] = useState([]);
  const navigate = useNavigate(); // For redirecting

  // Retrieve user ID from local storage
  useEffect(() => {
    const savedUser = localStorage.getItem("user");
    if (savedUser) {
      const parsedUser = JSON.parse(savedUser);
      setUserId(parsedUser.userId);
    }
  }, []);

  const handleChange = (index, e) => {
    const { name, value } = e.target;
    const newItems = [...items];
    newItems[index][name] = value;
    setItems(newItems);
  };

  const addItem = () => {
    setItems([...items, { itemNumber: "", quantity: 1 }]);
  };

  const removeItem = (index) => {
    setItems(items.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // 🚨 Prevent order submission if the user is not logged in
    if (!userId) {
      alert("You must be signed in to submit a request.");
      navigate("/login"); // Redirect to login page
      return;
    }

    if (!store) {
      alert("Please select a store.");
      return;
    }

    const storeId = storeMapping[store];

    const requestData = {
      userId,
      storeId,
      items: items.map(item => ({
        itemNumber: parseInt(item.itemNumber),
        quantity: parseInt(item.quantity),
      })),
      timeToWait: parseInt(timeToWait),
      notes,
    };

    try {
      const response = await fetch("http://127.0.0.1:5000/api/request", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestData),
      });

      const responseData = await response.json();

      if (response.ok) {
        alert("Order request submitted successfully!");
        setStore("");
        setItems([{ itemNumber: "", quantity: 1 }]);
        setTimeToWait("");
        setNotes("");
        setErrorItems([]);
      } else if (response.status === 400 && responseData.error === "Invalid item numbers") {
        console.log("❌ Invalid items received:", responseData.invalidItems);
        setErrorItems(responseData.invalidItems);
      } else {
        alert("Failed to submit request: " + (responseData.error || "Unknown error"));
      }
    } catch (error) {
      console.error("Error submitting request:", error);
      alert("An error occurred. Please try again.");
    }
  };

  return (
    <div className="request-order-container">
      <h2 className="request-title">Request an Order</h2>
      
      {/* 🚨 Show warning if user is not logged in */}
      {!userId && (
        <div className="alert alert-warning">
          ⚠️ You must be signed in to request an order. <button onClick={() => navigate("/login")} className="btn btn-link">Login here</button>
        </div>
      )}

      <form onSubmit={handleSubmit}>
        
        {/* Store Selection */}
        <div className="form-group">
          <label>Choose a Store:</label>
          <select value={store} onChange={(e) => setStore(e.target.value)} required>
            <option value="">Select a store</option>
            {Object.keys(storeMapping).map((storeName) => (
              <option key={storeName} value={storeName}>{storeName}</option>
            ))}
          </select>
        </div>

        {/* Items Section */}
        {items.map((item, index) => (
          <div key={index} className="form-group item-group">
            <label>Item Number:</label>
            <input
              type="number"
              name="itemNumber"
              value={item.itemNumber}
              onChange={(e) => handleChange(index, e)}
              required
            />
            {/* Error message appears on a separate line */}
            {errorItems.includes(parseInt(item.itemNumber)) && (
              <div className="error-text">❌ Invalid item number</div>
            )}

            <label>Quantity:</label>
            <input
              type="number"
              name="quantity"
              value={item.quantity}
              onChange={(e) => handleChange(index, e)}
              min="1"
              required
            />

            <button type="button" className="btn-remove" onClick={() => removeItem(index)}>
              Remove
            </button>
          </div>
        ))}

        <button type="button" className="btn-add" onClick={addItem}>
          + Add Another Item
        </button>

        {/* Time to Wait */}
        <div className="form-group">
          <label>Time to Wait (Days):</label>
          <input
            type="number"
            name="timeToWait"
            value={timeToWait}
            onChange={(e) => setTimeToWait(e.target.value)}
            min="0"
            required
          />
        </div>

        {/* Additional Notes */}
        <div className="form-group">
          <label>Additional Notes:</label>
          <textarea name="notes" value={notes} onChange={(e) => setNotes(e.target.value)} />
        </div>

        {/* Submit Button - Disabled if user is not logged in */}
        <button type="submit" className="btn btn-primary" disabled={!userId}>
          Submit Request
        </button>
      </form>
    </div>
  );
};

export default RequestOrder;
