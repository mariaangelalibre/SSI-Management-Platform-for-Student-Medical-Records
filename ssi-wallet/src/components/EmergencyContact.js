import React from 'react';
import '../styles/Health.css'; // Ensure the correct path to your CSS file

const HealthID = () => {
    return (
        <div className="background">
            <div className="wrapper">
                <div className="title">Emergency Contact Number</div>
                <div className="field-health">
                    <label>Name of Emergency Contact Person:</label>
                    <p>Fae Marie</p>
                </div>
                <div className="field-health">
                    <label>Contact Number:</label>
                    <p>09171234567</p>
                </div>
            </div>
        </div>
    );
};

export default HealthID;
