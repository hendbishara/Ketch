import React from "react";
import { Link } from "react-router-dom";
import "./header.css";
import Container from 'react-bootstrap/Container';
import Navbar from 'react-bootstrap/Navbar';
import Nav from 'react-bootstrap/Nav';

const Header = ({ user }) => {
  return (
    <Navbar className="bg-body-tertiary">
      <Container>
        <Navbar.Brand as={Link} to="/" style={{ fontSize: "3rem", fontWeight: "bold" }}>
          Ketch
        </Navbar.Brand>
        <Navbar.Toggle />
        <Navbar.Collapse className="justify-content-end">
          <Nav>
            <Nav.Link as={Link} to="/">Order Status</Nav.Link>
            <Nav.Link as={Link} to="/nearby-orders">Nearby Orders</Nav.Link>
            <Nav.Link as={Link} to="/request-order">Request Order</Nav.Link>
            <Nav.Link as={Link} to="/login">
              {user ? `Logged in as: ${user.name}` : "Login"}
            </Nav.Link>
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
};

export default Header;
