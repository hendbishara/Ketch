import React from "react";
import "./orderStatus.css";
import ProgressBar from "react-bootstrap/ProgressBar";
import Card from "react-bootstrap/Card";
import CardGroup from "react-bootstrap/CardGroup";


const orders = [
  {
    id: 1,
    status: "Order Listed",
    progress: 25,
    purchaseDate: "3/27/25",
    partners: "3 Partners",
    shop: "Room&Board",
    orderDate: "5/1/25",
    logo: "/assets/room&board_logo.png",
  },
  {
    id: 2,
    status: "Processing",
    progress: 50,
    purchaseDate: "4/10/25",
    partners: "2 Partners",
    shop: "IKEA",
    orderDate: "27/1/25",
    logo: "/assets/AllModern_logo.png",
  }
];

const OrderStatus = () => {
  return (
    <CardGroup className="d-flex flex-wrap justify-content-center">
      <h3 style={{ marginRight: "20px", fontSize: "1.5rem" }}> Orders Status </h3>
      {orders.map((order) => (
        <Card key={order.id} className="bg-light text-dark m-2 p-3 rounded-lg text-center" style={{ width: "300px" }}>
          <Card.Body>
            {/* Logo */}
            <div className="d-flex justify-content-center mb-2">
              <img src={order.logo} alt="Company Logo" className="rounded-circle" style={{ width: "40px", height: "40px" }} />
            </div>
            
            {/* Status & Shop Name */}
            <Card.Title className="mb-0">{order.status} <span className="text-muted">[{order.progress / 25}]</span></Card.Title>
            <Card.Subtitle className="text-muted mb-3">{order.shop}</Card.Subtitle>

            {/* Progress Bar */}
            <ProgressBar now={order.progress} variant="success" className="mt-2" />

            {/* Purchase & Order Date Info */}
            <Card.Text className="text-muted mt-2">
              Ordered on <strong>{order.orderDate}</strong><br/>
              Exp. Delivery <strong>{order.purchaseDate}</strong> | <strong>{order.partners}</strong>
            </Card.Text>
          </Card.Body>
        </Card>
      ))}
    </CardGroup>
  );
};

export default OrderStatus;
