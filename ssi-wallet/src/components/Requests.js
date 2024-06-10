import React from 'react';
import '../styles/Request.css'; 

const Requests = ({ authorizedInfo, handleAuthorize, handleDeny }) => {
    const clinicRequest = {
        clinicName: 'PUP CEA',
        requestedInfo: 'Blood Type',
    };

    return (
        <div className='background-req'>
            <div className="App">
                {authorizedInfo.length === 0 ? (
                    <div className="notification-box">
                        <div className="notification-content">
                            <p><strong>Clinic:{clinicRequest.clinicName}</strong></p>
                            <div className="requested-info">
                                <p>Requested Info:</p>
                                <div className="info-box">{clinicRequest.requestedInfo}</div>
                            </div>
                        </div>
                        <div className="notification-actions">
                            <button className="authorize" onClick={() => handleAuthorize(clinicRequest.requestedInfo)}>Authorize</button>
                            <button className="deny" onClick={handleDeny}>Deny</button>
                        </div>
                    </div>
                ) : (
                    <div className="authorized-box">
                        <p>Granted Authorization: {authorizedInfo.join(', ')}</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default Requests;
