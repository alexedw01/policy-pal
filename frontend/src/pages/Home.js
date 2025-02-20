import React from "react";
import { Link } from "react-router-dom";
import "./Home.css"; // for styling

const Home = () => {
  return (
    <div className="home-container">
      {/* Navbar */}
      <nav className="navbar">
        <h1 className="logo">PolicyPal</h1>
        <div className="nav-buttons">
          <Link to="/login" className="login-button">Login</Link>
          <Link to="/signup" className="signup-button">Sign Up</Link>
        </div>
      </nav>

      {/* Main Content */}
      <div className="home-content">
        <h1>Policy Pal</h1>
        <p>I Love Bill$!!!</p>
      </div>
    </div>
  );
};

export default Home;
