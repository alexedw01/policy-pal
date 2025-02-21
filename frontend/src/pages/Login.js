import React, { useState } from "react";
import { Link } from "react-router-dom";

const Login = () => {
  const [formData, setFormData] = useState({
    username: "",
    password: "",
  });

  const isValidUsername = /^[^\s]+$/.test(formData.username); // No spaces allowed
  const isFormValid = isValidUsername && formData.password.trim() !== "";

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (isFormValid) {
      console.log("Login Data:", formData);
      alert("Login form filled out correctly!");
    }
  };

  return (
    <div className="login-container" style={{ textAlign: "center", padding: "20px" }}>
      <h2>Login</h2>
      <form onSubmit={handleSubmit} style={{ display: "inline-block", textAlign: "left" }}>
        <input 
          type="text" 
          name="username" 
          placeholder="Username (no spaces)" 
          value={formData.username} 
          onChange={handleChange} 
          required 
          style={{ display: "block", margin: "10px 0", padding: "8px", width: "200px" }}
        />
        {!isValidUsername && formData.username && (
          <p style={{ color: "red", fontSize: "12px" }}>Username cannot contain spaces</p>
        )}
        <input 
          type="password" 
          name="password" 
          placeholder="Password" 
          value={formData.password} 
          onChange={handleChange} 
          required 
          style={{ display: "block", margin: "10px 0", padding: "8px", width: "200px" }}
        />
        <button 
          type="submit" 
          disabled={!isFormValid} 
          style={{ marginTop: "10px", padding: "10px 20px", backgroundColor: isFormValid ? "#ffa726" : "#ccc", border: "none", borderRadius: "5px", fontWeight: "bold", cursor: isFormValid ? "pointer" : "not-allowed" }}
        >
          Login
        </button>
      </form>
      <br />
      <Link to="/" style={{ marginTop: "20px", display: "inline-block", textDecoration: "none", color: "#007bff" }}>
        Back to Home
      </Link>
    </div>
  );
};

export default Login;
