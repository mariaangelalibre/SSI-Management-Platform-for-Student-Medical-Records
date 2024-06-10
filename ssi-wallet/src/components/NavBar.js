import React from 'react';
import '../styles/NavBar.css'; 

const NavBar = ({ setActivePage }) => {
  return (
    <nav className="green-navbar">
      <input type="checkbox" id="check" />
      <label htmlFor="check" className="checkbtn">
        <i className="fas fa-bars"></i>
      </label>
      <label className="logo">CEA Curekey</label>
      <ul>
        <li><a href="#" onClick={() => setActivePage('credentials')}>Credentials</a></li>
        <li><a href="#" onClick={() => setActivePage('requests')}>Requests</a></li>
      </ul>
    </nav>
  );
};

export default NavBar;
