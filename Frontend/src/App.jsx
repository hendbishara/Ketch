import { GoogleOAuthProvider } from "@react-oauth/google";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";  // ✅ Added Navigate here
import { useState, useEffect } from "react";
import Header from "./components/header/Header";
import OrderStatus from "./components/orderStatus/OrderStatus";
import NearbyOrders from "./components/nearbyOrders/NearbyOrders";
import RequestOrder from "./components/requestOrder/RequestOrder";
import Login from "./components/login/Login";
import "./App.css";
import "bootstrap/dist/css/bootstrap.min.css";

const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;

function App() {
  const [user, setUser] = useState(null);

  useEffect(() => {
    // Restore user from localStorage
    const savedUser = localStorage.getItem("user");
    if (savedUser) {
      setUser(JSON.parse(savedUser));
    }
  }, []);

  return (
    <GoogleOAuthProvider clientId={clientId}>
      <Router> {/* ✅ Wrap everything inside Router */}
        <Header user={user} />
        <Routes>
          <Route path="/" element={<Navigate to="/order-status" />} />  {/* Redirect to Order Status */}
          <Route path="/login" element={<Login setUser={setUser} />} />
          <Route path="/order-status" element={<OrderStatus />} />
          <Route path="/nearby-orders" element={<NearbyOrders />} />
          <Route path="/request-order" element={<RequestOrder />} />
          <Route path="*" element={<h1>404 - Page Not Found</h1>} />  {/* Catch-all for unknown routes */}
        </Routes>
      </Router>
    </GoogleOAuthProvider>
  );
}

export default App;
