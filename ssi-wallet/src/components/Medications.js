import React from 'react';
import '../styles/Health.css'; // Ensure the correct path to your CSS file

const Medications = () => {
    return (
        <div className="background">
            <div className="wrapper">
                <div className="title">Medications</div>
                <div className="field-health">
                    <label>COVID-19 vaccination status:</label>
                    <p>Vaccinated</p>
                </div>
                <div className="field-health">
                    <label>Types of Vaccine Doses:</label>
                    <p>1st Dose: Sinovac</p>
                    <p>2nd Dose: Sinovac</p>
                    <p>Booster: Sinovac</p>
                </div>
                <div className="field-health">
                    <label>Medications for maintenance:</label>
                    <p>Losartan</p>
                </div>
            </div>
        </div>
    );
};

export default Medications;
