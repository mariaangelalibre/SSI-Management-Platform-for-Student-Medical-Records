import React, { useState } from 'react';
import HealthID from './HealthID';
import Medications from './Medications';
import EmergencyContact from './EmergencyContact';
import '../styles/NavBar.css'; 

const Credentials = () => {
    const [activeTab, setActiveTab] = useState('healthID');

    return (
        <div>
            <nav className="black-navbar">
                <input type="checkbox" id="check" />
                <ul>
                    <li><a href="#" className={activeTab === 'healthID' ? 'active' : ''} onClick={() => setActiveTab('healthID')}>Health ID</a></li>
                    <li><a href="#" className={activeTab === 'medications' ? 'active' : ''} onClick={() => setActiveTab('medications')}>Medications</a></li>
                    <li><a href="#" className={activeTab === 'emergency' ? 'active' : ''} onClick={() => setActiveTab('emergency')}>Emergency Contact Number</a></li>
                </ul>
            </nav>
            {activeTab === 'healthID' && <HealthID />}
            {activeTab === 'medications' && <Medications />}
            {activeTab === 'emergency' && <EmergencyContact />}
        </div>

    );
};

export default Credentials;
