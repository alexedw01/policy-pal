import React, { useState } from "react";
import { Link } from "react-router-dom";

const SignUp = () => {
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log("Sign Up Data:", formData);
  };

  return (
    <div className="signup-container" style={{ textAlign: "center", padding: "20px" }}>
      <h2>Sign Up</h2>
      <form onSubmit={handleSubmit} style={{ display: "inline-block", textAlign: "left" }}>
        <input 
          type="text" 
          name="username" 
          placeholder="Username" 
          value={formData.username} 
          onChange={handleChange} 
          required 
          style={{ display: "block", margin: "10px 0", padding: "8px", width: "200px" }}
        />
        <input 
          type="email" 
          name="email" 
          placeholder="Email" 
          value={formData.email} 
          onChange={handleChange} 
          required 
          style={{ display: "block", margin: "10px 0", padding: "8px", width: "200px" }}
        />
        <input 
          type="password" 
          name="password" 
          placeholder="Password" 
          value={formData.password} 
          onChange={handleChange} 
          required 
          style={{ display: "block", margin: "10px 0", padding: "8px", width: "200px" }}
        />
        <button type="submit" style={{ marginTop: "10px", padding: "10px 20px", backgroundColor: "#61dafb", border: "none", borderRadius: "5px", fontWeight: "bold" }}>
          Sign Up
        </button>
      </form>
      <br />
      <Link to="/" style={{ marginTop: "20px", display: "inline-block", textDecoration: "none", color: "#007bff" }}>
        Back to Home
      </Link>
    </div>
  );
};

export default SignUp;
