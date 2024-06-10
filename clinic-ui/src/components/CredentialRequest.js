import React, { useState } from 'react';
import '../styles/Credentials.css';

const CredentialRequest = ({ student }) => {
    const [selectedCredentials, setSelectedCredentials] = useState({
        givenName: false,
        lastName: false,
        bloodType: false,
    });

    const handleCheckboxChange = (e) => {
        setSelectedCredentials({
            ...selectedCredentials,
            [e.target.name]: e.target.checked,
        });
    };

    const handleSelectAll = () => {
        const allSelected = Object.values(selectedCredentials).every(Boolean);
        setSelectedCredentials({
            givenName: !allSelected,
            lastName: !allSelected,
            bloodType: !allSelected,
        });
    };

    const handleRequest = () => {
        alert('Credential has been requested.');
    };

    return (
        <div className="credential-request-box">
            <h2 className="small-title">Request Medical Credentials for {student.name}</h2>
            <fieldset className="checkbox-box">
                <legend>Select Credentials</legend>
                <div className="checkbox-list">
                    <label>
                        <input
                            type="checkbox"
                            name="givenName"
                            checked={selectedCredentials.givenName}
                            onChange={handleCheckboxChange}
                        />
                        Given Name
                    </label>
                    <label>
                        <input
                            type="checkbox"
                            name="lastName"
                            checked={selectedCredentials.lastName}
                            onChange={handleCheckboxChange}
                        />
                        Last Name
                    </label>
                    <label>
                        <input
                            type="checkbox"
                            name="bloodType"
                            checked={selectedCredentials.bloodType}
                            onChange={handleCheckboxChange}
                        />
                        Blood Type
                    </label>
                </div>
            </fieldset>
            <div className="button-group">
                <button onClick={handleSelectAll}>Select All</button>
                <button onClick={handleRequest}>Request</button>
            </div>
        </div>
    );
};

export default CredentialRequest;
