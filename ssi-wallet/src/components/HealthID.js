import React from 'react';
import '../styles/Health.css'; // Ensure the correct path to your CSS file

const HealthID = () => {
    return (
        <div className="background">
            <div className="wrapper">
                <div className="title">Health Information</div>
                <div className="field-health">
                    <label>Given Name:</label>
                    <p>John</p>
                </div>
                <div className="field-health">
                    <label>Surname:</label>
                    <p>Doe</p>
                </div>
                <div className="field-health">
                    <label>Street Address:</label>
                    <p>123 Main St</p>
                </div>
                <div className="field-health">
                    <label>City:</label>
                    <p>Springfield</p>
                </div>
                <div className="field-health">
                    <label>Region:</label>
                    <p>Illinois</p>
                </div>
                <div className="field-health">
                    <label>Zip Code:</label>
                    <p>62701</p>
                </div>
                <div className="field-health">
                    <label>Country:</label>
                    <p>USA</p>
                </div>
                <div className="field-health">
                    <label>Nationality:</label>
                    <p>American</p>
                </div>
                <div className="field-health">
                    <label>Sex:</label>
                    <p>Male</p>
                </div>
                <div className="field-health">
                    <label>Gender:</label>
                    <p>Male</p>
                </div>
                <div className="field-health">
                    <label>Date of Birth:</label>
                    <p>01/01/1990</p>
                </div>
                <div className="field-health">
                    <label>Email:</label>
                    <p>john.doe@example.com</p>
                </div>
                <div className="field-health">
                    <label>Phone Number:</label>
                    <p>(555) 555-5555</p>
                </div>
                <div className="field-health">
                    <label>Comorbidity:</label>
                    <p>Hypertension, Diabetes</p>
                </div>
                <div className="field-health">
                    <label>Blood Type:</label>
                    <p>O+</p>
                </div>
                <div className="field-health">
                    <label>Disability (PWD):</label>
                    <p>None</p>
                </div>
            </div>
        </div>
    );
};

export default HealthID;
