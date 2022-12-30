import axios, { AxiosInstance } from "axios"

/**
 * Create an axios client that makes authenticated requests to the backend API by default.
 *
 * @param token jwt token to include in the Authorization header
 * @returns
 */
export const configureAxiosWithToken = (token: string): AxiosInstance => {
    const client = axios.create({
        headers: {
            'Authorization': token
        }
    })
    return client
}
