import React from "react";
import "./nearbyOrders.css";
import Card from "react-bootstrap/Card";
import CardGroup from "react-bootstrap/CardGroup";
import Button from "react-bootstrap/Button";  
const img1 = "/assets/img1.svg";

const NearbyOrders = () => {
  return (
    <div>
      <CardGroup>
        <h3 style={{ marginRight: "20px", fontSize: "1.5rem" }}> Nearby Orders </h3>
        <Card className="text-center">
          <div className="d-flex justify-content-center mt-3">
            <Card.Img
              variant="top"
              src={img1}
              style={{
                width: "200px",
                height: "200px",
                objectFit: "cover",
              }}
            />
          </div>
          <Card.Body>
            <Card.Title>West Elm</Card.Title>
            <div className="price-container">
              <span className="original-price">$65</span>
              <span className="discounted-price">$22</span>
            </div>
            <Card.Text>
              Purchase Date: 22.03.2025 <br />
              Partners Number: 4
            </Card.Text>
          </Card.Body>
          <Card.Footer>
            <Button variant="primary">Join Order</Button>
          </Card.Footer>
        </Card>

      </CardGroup>
    </div>
  );
};

export default NearbyOrders;
