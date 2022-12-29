// react component
import React from 'react';

// read the cognito idToken from the browser
import { getUserIdToken } from '../aws-cognito/auth-utils';



const ServerDeprovisioning = () => {

    // use and effect hook to read the token
    React.useEffect(() => {
        getUserIdToken()
            .then((idToken) => {
                console.log("The idToken is: ", idToken)
            })
            .catch((error) => {
                console.log("Error reading token: ", error)
            })
    }, []);

    return (
        <div>
            <h1>Server is shutting down</h1>
        </div>
    );
};

export default ServerDeprovisioning;
