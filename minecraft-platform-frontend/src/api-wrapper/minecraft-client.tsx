/**
 * Helper functions that use the generated src/api/ code to make requests to the backend API.
 *
 * Note: these functions currently do not handle errors, but they should. We wrote these
 * the way they are to quickly get an MVP working, but the way these are written, users
 * will have no idea if errors occur.
 */

import { AxiosResponse } from "axios";
import { DeploymentStatus, DeploymentStatusResponse, DestroyServer, MinecraftServerApi, ServerIpSchema, StartServerRequestPayload } from "../api/api";
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


export const startMinecraftServer = async (args: {
    minecraftClient: MinecraftServerApi,
    hours: number,
    serverSize: string,
    allowRisk: boolean,
}) => {
    const { minecraftClient, hours, serverSize, allowRisk } = args;

    const minutesOfServerUptime = hours * 60;
    const payload: StartServerRequestPayload = {
        play_time_minutes: minutesOfServerUptime
    }

    const response: AxiosResponse<DeploymentStatusResponse> = await minecraftClient.startMinecraftServerMinecraftServerPost(payload)
    return response.data.status;
}

export const getMinecraftServerIpAddress = async (args: {
    minecraftClient: MinecraftServerApi,
}): Promise<string> => {
    const { minecraftClient } = args;
    const response: AxiosResponse<ServerIpSchema> = await minecraftClient.getMinecraftServerIpAddressMinecraftServerIpAddressGet();
    return response.data.server_ip_address;
}

export const stopMinecraftServer = async (args: {
    minecraftClient: MinecraftServerApi,
}): Promise<DeploymentStatus> => {
    const { minecraftClient } = args;
    const payload: DestroyServer = {}
    const response: AxiosResponse<DeploymentStatusResponse> = await minecraftClient.stopMinecraftServerMinecraftServerDelete(payload);
    return response.data.status;
}

export const getServerStatus = async (minecraftClient: MinecraftServerApi): Promise<DeploymentStatus | null> => {
    if (minecraftClient) {
        const response: AxiosResponse<DeploymentStatusResponse> = await minecraftClient.getMinecraftServerDeploymentStatusMinecraftServerStatusGet();
        return response.data.status
    }
    return null
}
