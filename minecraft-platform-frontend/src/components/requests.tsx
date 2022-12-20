import axios from "axios";

export async function getAPIRequest(getCallType: string, serverUrl=getServerUrl()) {
    try {
        return await axios.get(`${serverUrl}/${getCallType}`)
    }
    catch(error: any) {
        return error.response;
    }
}

const getServerUrl = () => {
    let url;
    switch(process.env.REACT_APP_ENVIRONMENT) {
        case 'production':
            url = 'http://0.0.0.0:80';
            break;
        case 'development':
            url = 'http://0.0.0.0:8000';
    }
    return url;
}
