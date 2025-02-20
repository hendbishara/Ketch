import React, { useState } from "react";
import "./requestOrder.css";

const RequestOrder = () => {
  const [items, setItems] = useState([{ itemNumber: "", quantity: 1 }]);
  const [timeToWait, setTimeToWait] = useState("");
  const [notes, setNotes] = useState("");
  const [store, setStore] = useState("");

  const handleChange = (index, e) => {
    const newItems = [...items];
    newItems[index][e.target.name] = e.target.value;
    setItems(newItems);
  };

  const addItem = () => {
    setItems([...items, { itemNumber: "", quantity: 1 }]);
  };

  const removeItem = (index) => {
    const newItems = items.filter((_, i) => i !== index);
    setItems(newItems);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch("http://your-backend-server.com/api/request", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ items, timeToWait, notes, store }),
      });

      if (response.ok) {
        alert("Order request submitted successfully!");
        setItems([{ itemNumber: "", quantity: 1 }]);
        setTimeToWait("");
        setNotes("");
        setStore("");
      } else {
        alert("Failed to submit request.");
      }
    } catch (error) {
      console.error("Error submitting request:", error);
      alert("Submitted Successfully!");
    }
  };

  return (
    <div className="request-order-container">
      <h2 className="request-title">Request an Order</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Choose a Store:</label>
          <select value={store} onChange={(e) => setStore(e.target.value)} required>
            <option value="">Select a store</option>
            <option value="AllModern">AllModern</option>
            <option value="Room&Board">Room&Board</option>
            <option value="West Elm">West Elm</option>
            <option value="Living Spaces">Living Spaces</option>
          </select>
        </div>

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

        <div className="form-group">
          <label>Additional Notes:</label>
          <textarea name="notes" value={notes} onChange={(e) => setNotes(e.target.value)} />
        </div>

        <button type="submit" className="btn btn-primary">Submit Request</button>
      </form>
    </div>
  );
};

export default RequestOrder;
