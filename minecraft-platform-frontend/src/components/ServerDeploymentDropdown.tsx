import React, {useState} from "react";
import {getAPIRequest} from "./requests";
import {Container} from "react-bootstrap";
import Form from "react-bootstrap/Form";

export const ServerDeploymentDropDown = () => {
    const [serverResponseData, setResponse] = useState("");
    const handleClick = (api_request: string) => {
        getAPIRequest(api_request).then(response => {
            console.log(response);
            setResponse(response.data);
        })
    }
    return (
        <Container>
            <Form.Select aria-label="Default select example" onChange={e => handleClick(e.target.value)}>
                <option value="status">Get API Status</option>
                <option value="deploy">Deploy Server</option>
                <option value="destroy">Destroy Server</option>
                <option value="latest-execution">Get Latest Execution</option>
                <option value="state-machine-status">Get Deployment Status</option>
            </Form.Select>
        <p>{JSON.stringify(serverResponseData)}</p>
        </Container>
  );
}
