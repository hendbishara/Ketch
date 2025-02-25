import React, { useEffect, useState } from "react";
import "./nearbyOrders.css";
import Card from "react-bootstrap/Card";
import Button from "react-bootstrap/Button";

// Store logo mapping
const storeLogos = {
  "AllModern": "/assets/AllModern_logo.png",
  "Room&Board": "/assets/room&board_logo.png",
  "West Elm": "/assets/west_elm_logo.jpeg",
  "Living Spaces": "/assets/living_spaces_logo.png"
};

// Default order data (always shown)
const defaultOrder = {
  storeName: "West Elm",
  originalPrice: 65,
  discountedPrice: 22,
  partnersNumber: 4,
  image: "/assets/west_elm_logo.jpeg"
};

const NearbyOrders = () => {
  const [nearbyOrders, setNearbyOrders] = useState([]);
  const [userId, setUserId] = useState(null);

  useEffect(() => {
    // Retrieve user ID from localStorage
    const savedUser = localStorage.getItem("user");
    if (savedUser) {
      const parsedUser = JSON.parse(savedUser);
      setUserId(parsedUser.userId);
    }
  }, []);

  useEffect(() => {
    if (!userId) return; // Don't fetch if user is not logged in

    const fetchNearbyOrders = async () => {
      try {
        const response = await fetch(`http://127.0.0.1:5000/api/nearby-orders?userId=${userId}`);
        const data = await response.json();

        if (response.ok) {
          setNearbyOrders(data.nearbyOrders);
        } else {
          console.error("Error fetching nearby orders:", data.error);
        }
      } catch (error) {
        console.error("Network error:", error);
      }
    };

    fetchNearbyOrders();
  }, [userId]);

  return (
    <div className="nearby-orders-container">
      <h3 style={{ marginBottom: "20px", fontSize: "1.5rem", textAlign: "center" }}>Nearby Orders</h3>

      {/* Orders Container with Flexbox */}
      <div className="orders-grid">
        {/* Default Order Card (Always Shown) */}
        <Card className="order-card text-center">
          <div className="d-flex justify-content-center mt-3">
            <Card.Img
              variant="top"
              src={defaultOrder.image}
              className="order-image"
            />
          </div>
          <Card.Body>
            <Card.Title>{defaultOrder.storeName}</Card.Title>
            <div className="price-container">
              <span className="original-price">${defaultOrder.originalPrice.toFixed(2)}</span>
              <span className="discounted-price">${defaultOrder.discountedPrice.toFixed(2)}</span>
            </div>
            <Card.Text>Partners Number: {defaultOrder.partnersNumber}</Card.Text>
          </Card.Body>
          <Card.Footer>
            <Button variant="primary">Join Order</Button>
          </Card.Footer>
        </Card>

        {/* Dynamic Nearby Orders */}
        {nearbyOrders.map((order, index) => (
          <Card className="order-card text-center" key={index}>
            <div className="d-flex justify-content-center mt-3">
              <Card.Img
                variant="top"
                src={storeLogos[order.storeName] || "/assets/img1.svg"}
                className="order-image"
              />
            </div>
            <Card.Body>
              <Card.Title>{order.storeName}</Card.Title>
              <div className="price-container">
                <span className="original-price">${order.originalPrice.toFixed(2)}</span>
                <span className="discounted-price">${order.discountedPrice.toFixed(2)}</span>
              </div>
              <Card.Text>Partners Number: {order.partnersNumber}</Card.Text>
            </Card.Body>
            <Card.Footer>
              <Button variant="primary">Join Order</Button>
            </Card.Footer>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default NearbyOrders;
