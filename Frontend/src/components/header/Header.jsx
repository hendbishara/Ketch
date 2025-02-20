import React from "react";
import "./header.css";
import Container from 'react-bootstrap/Container';
import Nav from 'react-bootstrap/Nav';
import Navbar from 'react-bootstrap/Navbar';
import NavDropdown from 'react-bootstrap/NavDropdown';


const Header = () => {
  return (
    <div>
    <Navbar className="bg-body-tertiary">
        <Container>
            <Navbar.Brand href="#home" style={{fontSize: "3rem" , fontWeight: "bold"}}>Ketch</Navbar.Brand>
            <Navbar.Toggle />
            <Navbar.Collapse className="justify-content-end">
            <Navbar.Text>
                Signed in as: <a href="#login">Jad Mahajne</a>
            </Navbar.Text>
            </Navbar.Collapse>
        </Container>
    </Navbar>
    </div>
  );
};

export default Header;