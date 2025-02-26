import React, { useEffect, useState } from "react";
import "./orderStatus.css";
import ProgressBar from "react-bootstrap/ProgressBar";
import Card from "react-bootstrap/Card";

// Default Order Data (Always Shown)
const defaultOrders = [
  {
    id: "default1",
    status: "Order Listed",
    progress: 25,
    orderDate: "01/19/25",
    shop: "West Elm",
    logo: "/assets/west_elm_logo.jpeg",
  },
  {
    id: "default2",
    status: "Order Processed",
    progress: 75,
    orderDate: "01/20/25",
    shop: "AllModern",
    logo: "/assets/AllModern_logo.png",
  }
];

const OrderStatus = () => {
  const [orders, setOrders] = useState([]);
  const [userId, setUserId] = useState(null);

  // Retrieve user ID from localStorage
  useEffect(() => {
    const savedUser = localStorage.getItem("user");
    if (savedUser) {
      const parsedUser = JSON.parse(savedUser);
      setUserId(parsedUser.userId);
    }
  }, []);

  useEffect(() => {
    if (!userId) return;

    const fetchOrders = async () => {
      try {
        const response = await fetch(`http://127.0.0.1:5000/api/user-orders?userId=${userId}`);
        const data = await response.json();

        if (response.ok) {
          setOrders(data.orders);
        } else {
          console.error("Error fetching orders:", data.error);
        }
      } catch (error) {
        console.error("Network error:", error);
      }
    };

    fetchOrders();
  }, [userId]);

  return (
    <div className="order-container">
      <h3 style={{ width: "100%", textAlign: "center", fontSize: "1.5rem" }}> Orders Status </h3>

      {/* Default Orders (Always Shown) */}
      {defaultOrders.map((order) => (
        <Card key={order.id} className="order-card bg-light text-dark p-3 rounded-lg text-center">
          <Card.Body>
            <div className="d-flex justify-content-center mb-2">
              <img src={order.logo} alt="Company Logo" className="rounded-circle" style={{ width: "40px", height: "40px" }} />
            </div>
            <Card.Title className="mb-0">{order.status} <span className="text-muted">[{order.progress}%]</span></Card.Title>
            <Card.Subtitle className="text-muted mb-3">{order.shop}</Card.Subtitle>
            <ProgressBar now={order.progress} variant="success" className="mt-2" />
            <Card.Text className="text-muted mt-2">
              Ordered on <strong>{order.orderDate}</strong>
            </Card.Text>
          </Card.Body>
        </Card>
      ))}

      {/* User Orders (Fetched from API) */}
      {orders.length > 0 ? (
        orders.map((order) => (
          <Card key={order.id} className="order-card bg-light text-dark p-3 rounded-lg text-center">
            <Card.Body>
              <div className="d-flex justify-content-center mb-2">
                <img src={order.logo} alt="Company Logo" className="rounded-circle" style={{ width: "40px", height: "40px" }} />
              </div>
              <Card.Title className="mb-0">{order.status} <span className="text-muted">[{order.progress}%]</span></Card.Title>
              <Card.Subtitle className="text-muted mb-3">{order.shop}</Card.Subtitle>
              <ProgressBar now={order.progress} variant="success" className="mt-2" />
              <Card.Text className="text-muted mt-2">
                {/* ✅ Change "Ordered on" or "Processed on" based on request status */}
                {order.status === "Order Listed" ? "Ordered on" : "Processed on"} <strong>{order.orderDate}</strong>
              </Card.Text>
            </Card.Body>
          </Card>
        ))
      ) : (
        <p style={{ width: "100%", textAlign: "center" }}>No active orders found other than the default orders.</p>
      )}
    </div>
  );
};

export default OrderStatus;
