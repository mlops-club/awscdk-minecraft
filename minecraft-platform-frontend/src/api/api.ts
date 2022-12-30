/* tslint:disable */
/* eslint-disable */
/**
 * 🎁 Minecraft Platform-as-a-Service API 🎄
 * A FastAPI app for the Minecraft API.
 *
 * The version of the OpenAPI document: 0.0.1
 *
 *
 * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).
 * https://openapi-generator.tech
 * Do not edit the class manually.
 */


import { Configuration } from './configuration';
import globalAxios, { AxiosPromise, AxiosInstance, AxiosRequestConfig } from 'axios';
// Some imports not used depending on template conditions
// @ts-ignore
import { DUMMY_BASE_URL, assertParamExists, setApiKeyToObject, setBasicAuthToObject, setBearerAuthToObject, setOAuthToObject, setSearchParams, serializeDataIfNeeded, toPathString, createRequestFunction } from './common';
// @ts-ignore
import { BASE_PATH, COLLECTION_FORMATS, RequestArgs, BaseAPI, RequiredError } from './base';

/**
 * State that the deployment currently occupies.
 * @export
 * @enum {string}
 */

export const DeploymentStatus = {
    Offline: 'SERVER_OFFLINE',
    Provisioning: 'SERVER_PROVISIONING',
    Online: 'SERVER_ONLINE',
    Deprovisioning: 'SERVER_DEPROVISIONING',
    ProvisioningFailed: 'SERVER_PROVISIONING_FAILED',
    DeprovisioningFailed: 'SERVER_DEPROVISIONING_FAILED'
} as const;

export type DeploymentStatus = typeof DeploymentStatus[keyof typeof DeploymentStatus];


/**
 * Response model for the `/deployment-status` endpoint.
 * @export
 * @interface DeploymentStatusResponse
 */
export interface DeploymentStatusResponse {
    /**
     * Current state of the minecraft server.
     * @type {DeploymentStatus}
     * @memberof DeploymentStatusResponse
     */
    'status': DeploymentStatus;
}
/**
 * Response model for the `/destroy-server-after-seconds` endpoint.
 * @export
 * @interface DestroyServer
 */
export interface DestroyServer {
    /**
     *
     * @type {number}
     * @memberof DestroyServer
     */
    'wait_n_minutes_before_destroy'?: number;
}
/**
 *
 * @export
 * @interface HTTPValidationError
 */
export interface HTTPValidationError {
    /**
     *
     * @type {Array<ValidationError>}
     * @memberof HTTPValidationError
     */
    'detail'?: Array<ValidationError>;
}
/**
 *
 * @export
 * @interface LocationInner
 */
export interface LocationInner {
}
/**
 * Response model for the `/minecraft-server-ip-address` endpoint.
 * @export
 * @interface ServerIpSchema
 */
export interface ServerIpSchema {
    /**
     * IPv4 address of the minecraft server.
     * @type {string}
     * @memberof ServerIpSchema
     */
    'server_ip_address': string;
}
/**
 * Response model for the `/destroy-server-after-seconds` endpoint.
 * @export
 * @interface StartServerRequestPayload
 */
export interface StartServerRequestPayload {
    /**
     *
     * @type {number}
     * @memberof StartServerRequestPayload
     */
    'play_time_minutes': number;
}
/**
 *
 * @export
 * @interface ValidationError
 */
export interface ValidationError {
    /**
     *
     * @type {Array<LocationInner>}
     * @memberof ValidationError
     */
    'loc': Array<LocationInner>;
    /**
     *
     * @type {string}
     * @memberof ValidationError
     */
    'msg': string;
    /**
     *
     * @type {string}
     * @memberof ValidationError
     */
    'type': string;
}

/**
 * AdminApi - axios parameter creator
 * @export
 */
export const AdminApiAxiosParamCreator = function (configuration?: Configuration) {
    return {
        /**
         * Return 200 to demonstrate that this REST API is reachable and can execute.
         * @summary Ping This Api
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        pingThisApiHealthcheckGet: async (options: AxiosRequestConfig = {}): Promise<RequestArgs> => {
            const localVarPath = `/healthcheck`;
            // use dummy base URL string because the URL constructor only accepts absolute URLs.
            const localVarUrlObj = new URL(localVarPath, DUMMY_BASE_URL);
            let baseOptions;
            if (configuration) {
                baseOptions = configuration.baseOptions;
            }

            const localVarRequestOptions = { method: 'GET', ...baseOptions, ...options};
            const localVarHeaderParameter = {} as any;
            const localVarQueryParameter = {} as any;



            setSearchParams(localVarUrlObj, localVarQueryParameter);
            let headersFromBaseOptions = baseOptions && baseOptions.headers ? baseOptions.headers : {};
            localVarRequestOptions.headers = {...localVarHeaderParameter, ...headersFromBaseOptions, ...options.headers};

            return {
                url: toPathString(localVarUrlObj),
                options: localVarRequestOptions,
            };
        },
    }
};

/**
 * AdminApi - functional programming interface
 * @export
 */
export const AdminApiFp = function(configuration?: Configuration) {
    const localVarAxiosParamCreator = AdminApiAxiosParamCreator(configuration)
    return {
        /**
         * Return 200 to demonstrate that this REST API is reachable and can execute.
         * @summary Ping This Api
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        async pingThisApiHealthcheckGet(options?: AxiosRequestConfig): Promise<(axios?: AxiosInstance, basePath?: string) => AxiosPromise<any>> {
            const localVarAxiosArgs = await localVarAxiosParamCreator.pingThisApiHealthcheckGet(options);
            return createRequestFunction(localVarAxiosArgs, globalAxios, BASE_PATH, configuration);
        },
    }
};

/**
 * AdminApi - factory interface
 * @export
 */
export const AdminApiFactory = function (configuration?: Configuration, basePath?: string, axios?: AxiosInstance) {
    const localVarFp = AdminApiFp(configuration)
    return {
        /**
         * Return 200 to demonstrate that this REST API is reachable and can execute.
         * @summary Ping This Api
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        pingThisApiHealthcheckGet(options?: any): AxiosPromise<any> {
            return localVarFp.pingThisApiHealthcheckGet(options).then((request) => request(axios, basePath));
        },
    };
};

/**
 * AdminApi - object-oriented interface
 * @export
 * @class AdminApi
 * @extends {BaseAPI}
 */
export class AdminApi extends BaseAPI {
    /**
     * Return 200 to demonstrate that this REST API is reachable and can execute.
     * @summary Ping This Api
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     * @memberof AdminApi
     */
    public pingThisApiHealthcheckGet(options?: AxiosRequestConfig) {
        return AdminApiFp(this.configuration).pingThisApiHealthcheckGet(options).then((request) => request(this.axios, this.basePath));
    }
}


/**
 * MinecraftServerApi - axios parameter creator
 * @export
 */
export const MinecraftServerApiAxiosParamCreator = function (configuration?: Configuration) {
    return {
        /**
         * Describe the current state of the minecraft deployment.  Deployment can be in any of 6 states:  | State | Description | | --- | --- | | `SERVER_OFFLINE` | The `awscdk-minecraft-server` CloudFormation stack does not exist or is in a `DELETE_COMPLETE` state. | | `SERVER_PROVISIONING` | The latest execution of the `provision-minecraft-server` Step Function state machine is in a `RUNNING` state. | | `SERVER_PROVISIONING_FAILED` | The latest execution of the `provision-minecraft-server` Step Function state machine is in a `FAILED` state. | | `SERVER_ONLINE` | The `awscdk-minecraft-server` CloudFormation stack exists and is in a `CREATE_COMPLETE` state. | | `SERVER_DEPROVISIONING` | The latest execution of the `deprovision-minecraft-server` AWS Step Function state machine is in a `RUNNING` state AND the execution does not have a `wait_n_minutes_before_deprovisioning` input parameter. | | `SERVER_DEPROVISIONING_FAILED` | The latest execution of the `deprovision-minecraft-server` AWS Step Function state machine. |  Depending on which `FAILED` state is the most recent, the status will be `SERVER_PROVISIONING_FAILED` or `SERVER_DEPROVISIONING_FAILED`.
         * @summary Get Minecraft Server Deployment Status
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        getMinecraftServerDeploymentStatusMinecraftServerStatusGet: async (options: AxiosRequestConfig = {}): Promise<RequestArgs> => {
            const localVarPath = `/minecraft-server/status`;
            // use dummy base URL string because the URL constructor only accepts absolute URLs.
            const localVarUrlObj = new URL(localVarPath, DUMMY_BASE_URL);
            let baseOptions;
            if (configuration) {
                baseOptions = configuration.baseOptions;
            }

            const localVarRequestOptions = { method: 'GET', ...baseOptions, ...options};
            const localVarHeaderParameter = {} as any;
            const localVarQueryParameter = {} as any;



            setSearchParams(localVarUrlObj, localVarQueryParameter);
            let headersFromBaseOptions = baseOptions && baseOptions.headers ? baseOptions.headers : {};
            localVarRequestOptions.headers = {...localVarHeaderParameter, ...headersFromBaseOptions, ...options.headers};

            return {
                url: toPathString(localVarUrlObj),
                options: localVarRequestOptions,
            };
        },
        /**
         * Get the minecraft server ip address.
         * @summary Get Minecraft Server Ip Address
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        getMinecraftServerIpAddressMinecraftServerIpAddressGet: async (options: AxiosRequestConfig = {}): Promise<RequestArgs> => {
            const localVarPath = `/minecraft-server/ip-address`;
            // use dummy base URL string because the URL constructor only accepts absolute URLs.
            const localVarUrlObj = new URL(localVarPath, DUMMY_BASE_URL);
            let baseOptions;
            if (configuration) {
                baseOptions = configuration.baseOptions;
            }

            const localVarRequestOptions = { method: 'GET', ...baseOptions, ...options};
            const localVarHeaderParameter = {} as any;
            const localVarQueryParameter = {} as any;



            setSearchParams(localVarUrlObj, localVarQueryParameter);
            let headersFromBaseOptions = baseOptions && baseOptions.headers ? baseOptions.headers : {};
            localVarRequestOptions.headers = {...localVarHeaderParameter, ...headersFromBaseOptions, ...options.headers};

            return {
                url: toPathString(localVarUrlObj),
                options: localVarRequestOptions,
            };
        },
        /**
         * Start the server if it is not already running.
         * @summary Start Minecraft Server
         * @param {StartServerRequestPayload} startServerRequestPayload
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        startMinecraftServerMinecraftServerPost: async (startServerRequestPayload: StartServerRequestPayload, options: AxiosRequestConfig = {}): Promise<RequestArgs> => {
            // verify required parameter 'startServerRequestPayload' is not null or undefined
            assertParamExists('startMinecraftServerMinecraftServerPost', 'startServerRequestPayload', startServerRequestPayload)
            const localVarPath = `/minecraft-server`;
            // use dummy base URL string because the URL constructor only accepts absolute URLs.
            const localVarUrlObj = new URL(localVarPath, DUMMY_BASE_URL);
            let baseOptions;
            if (configuration) {
                baseOptions = configuration.baseOptions;
            }

            const localVarRequestOptions = { method: 'POST', ...baseOptions, ...options};
            const localVarHeaderParameter = {} as any;
            const localVarQueryParameter = {} as any;



            localVarHeaderParameter['Content-Type'] = 'application/json';

            setSearchParams(localVarUrlObj, localVarQueryParameter);
            let headersFromBaseOptions = baseOptions && baseOptions.headers ? baseOptions.headers : {};
            localVarRequestOptions.headers = {...localVarHeaderParameter, ...headersFromBaseOptions, ...options.headers};
            localVarRequestOptions.data = serializeDataIfNeeded(startServerRequestPayload, localVarRequestOptions, configuration)

            return {
                url: toPathString(localVarUrlObj),
                options: localVarRequestOptions,
            };
        },
        /**
         * Stop the server if it is running.  If the `wait_n_minutes_before_destroy` parameter is set, the server will be stopped after the specified amount of time. Otherwise the server will be stopped immediately.
         * @summary Stop Minecraft Server
         * @param {DestroyServer} destroyServer
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        stopMinecraftServerMinecraftServerDelete: async (destroyServer: DestroyServer, options: AxiosRequestConfig = {}): Promise<RequestArgs> => {
            // verify required parameter 'destroyServer' is not null or undefined
            assertParamExists('stopMinecraftServerMinecraftServerDelete', 'destroyServer', destroyServer)
            const localVarPath = `/minecraft-server`;
            // use dummy base URL string because the URL constructor only accepts absolute URLs.
            const localVarUrlObj = new URL(localVarPath, DUMMY_BASE_URL);
            let baseOptions;
            if (configuration) {
                baseOptions = configuration.baseOptions;
            }

            const localVarRequestOptions = { method: 'DELETE', ...baseOptions, ...options};
            const localVarHeaderParameter = {} as any;
            const localVarQueryParameter = {} as any;



            localVarHeaderParameter['Content-Type'] = 'application/json';

            setSearchParams(localVarUrlObj, localVarQueryParameter);
            let headersFromBaseOptions = baseOptions && baseOptions.headers ? baseOptions.headers : {};
            localVarRequestOptions.headers = {...localVarHeaderParameter, ...headersFromBaseOptions, ...options.headers};
            localVarRequestOptions.data = serializeDataIfNeeded(destroyServer, localVarRequestOptions, configuration)

            return {
                url: toPathString(localVarUrlObj),
                options: localVarRequestOptions,
            };
        },
    }
};

/**
 * MinecraftServerApi - functional programming interface
 * @export
 */
export const MinecraftServerApiFp = function(configuration?: Configuration) {
    const localVarAxiosParamCreator = MinecraftServerApiAxiosParamCreator(configuration)
    return {
        /**
         * Describe the current state of the minecraft deployment.  Deployment can be in any of 6 states:  | State | Description | | --- | --- | | `SERVER_OFFLINE` | The `awscdk-minecraft-server` CloudFormation stack does not exist or is in a `DELETE_COMPLETE` state. | | `SERVER_PROVISIONING` | The latest execution of the `provision-minecraft-server` Step Function state machine is in a `RUNNING` state. | | `SERVER_PROVISIONING_FAILED` | The latest execution of the `provision-minecraft-server` Step Function state machine is in a `FAILED` state. | | `SERVER_ONLINE` | The `awscdk-minecraft-server` CloudFormation stack exists and is in a `CREATE_COMPLETE` state. | | `SERVER_DEPROVISIONING` | The latest execution of the `deprovision-minecraft-server` AWS Step Function state machine is in a `RUNNING` state AND the execution does not have a `wait_n_minutes_before_deprovisioning` input parameter. | | `SERVER_DEPROVISIONING_FAILED` | The latest execution of the `deprovision-minecraft-server` AWS Step Function state machine. |  Depending on which `FAILED` state is the most recent, the status will be `SERVER_PROVISIONING_FAILED` or `SERVER_DEPROVISIONING_FAILED`.
         * @summary Get Minecraft Server Deployment Status
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        async getMinecraftServerDeploymentStatusMinecraftServerStatusGet(options?: AxiosRequestConfig): Promise<(axios?: AxiosInstance, basePath?: string) => AxiosPromise<DeploymentStatusResponse>> {
            const localVarAxiosArgs = await localVarAxiosParamCreator.getMinecraftServerDeploymentStatusMinecraftServerStatusGet(options);
            return createRequestFunction(localVarAxiosArgs, globalAxios, BASE_PATH, configuration);
        },
        /**
         * Get the minecraft server ip address.
         * @summary Get Minecraft Server Ip Address
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        async getMinecraftServerIpAddressMinecraftServerIpAddressGet(options?: AxiosRequestConfig): Promise<(axios?: AxiosInstance, basePath?: string) => AxiosPromise<ServerIpSchema>> {
            const localVarAxiosArgs = await localVarAxiosParamCreator.getMinecraftServerIpAddressMinecraftServerIpAddressGet(options);
            return createRequestFunction(localVarAxiosArgs, globalAxios, BASE_PATH, configuration);
        },
        /**
         * Start the server if it is not already running.
         * @summary Start Minecraft Server
         * @param {StartServerRequestPayload} startServerRequestPayload
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        async startMinecraftServerMinecraftServerPost(startServerRequestPayload: StartServerRequestPayload, options?: AxiosRequestConfig): Promise<(axios?: AxiosInstance, basePath?: string) => AxiosPromise<DeploymentStatusResponse>> {
            const localVarAxiosArgs = await localVarAxiosParamCreator.startMinecraftServerMinecraftServerPost(startServerRequestPayload, options);
            return createRequestFunction(localVarAxiosArgs, globalAxios, BASE_PATH, configuration);
        },
        /**
         * Stop the server if it is running.  If the `wait_n_minutes_before_destroy` parameter is set, the server will be stopped after the specified amount of time. Otherwise the server will be stopped immediately.
         * @summary Stop Minecraft Server
         * @param {DestroyServer} destroyServer
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        async stopMinecraftServerMinecraftServerDelete(destroyServer: DestroyServer, options?: AxiosRequestConfig): Promise<(axios?: AxiosInstance, basePath?: string) => AxiosPromise<DeploymentStatusResponse>> {
            const localVarAxiosArgs = await localVarAxiosParamCreator.stopMinecraftServerMinecraftServerDelete(destroyServer, options);
            return createRequestFunction(localVarAxiosArgs, globalAxios, BASE_PATH, configuration);
        },
    }
};

/**
 * MinecraftServerApi - factory interface
 * @export
 */
export const MinecraftServerApiFactory = function (configuration?: Configuration, basePath?: string, axios?: AxiosInstance) {
    const localVarFp = MinecraftServerApiFp(configuration)
    return {
        /**
         * Describe the current state of the minecraft deployment.  Deployment can be in any of 6 states:  | State | Description | | --- | --- | | `SERVER_OFFLINE` | The `awscdk-minecraft-server` CloudFormation stack does not exist or is in a `DELETE_COMPLETE` state. | | `SERVER_PROVISIONING` | The latest execution of the `provision-minecraft-server` Step Function state machine is in a `RUNNING` state. | | `SERVER_PROVISIONING_FAILED` | The latest execution of the `provision-minecraft-server` Step Function state machine is in a `FAILED` state. | | `SERVER_ONLINE` | The `awscdk-minecraft-server` CloudFormation stack exists and is in a `CREATE_COMPLETE` state. | | `SERVER_DEPROVISIONING` | The latest execution of the `deprovision-minecraft-server` AWS Step Function state machine is in a `RUNNING` state AND the execution does not have a `wait_n_minutes_before_deprovisioning` input parameter. | | `SERVER_DEPROVISIONING_FAILED` | The latest execution of the `deprovision-minecraft-server` AWS Step Function state machine. |  Depending on which `FAILED` state is the most recent, the status will be `SERVER_PROVISIONING_FAILED` or `SERVER_DEPROVISIONING_FAILED`.
         * @summary Get Minecraft Server Deployment Status
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        getMinecraftServerDeploymentStatusMinecraftServerStatusGet(options?: any): AxiosPromise<DeploymentStatusResponse> {
            return localVarFp.getMinecraftServerDeploymentStatusMinecraftServerStatusGet(options).then((request) => request(axios, basePath));
        },
        /**
         * Get the minecraft server ip address.
         * @summary Get Minecraft Server Ip Address
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        getMinecraftServerIpAddressMinecraftServerIpAddressGet(options?: any): AxiosPromise<ServerIpSchema> {
            return localVarFp.getMinecraftServerIpAddressMinecraftServerIpAddressGet(options).then((request) => request(axios, basePath));
        },
        /**
         * Start the server if it is not already running.
         * @summary Start Minecraft Server
         * @param {StartServerRequestPayload} startServerRequestPayload
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        startMinecraftServerMinecraftServerPost(startServerRequestPayload: StartServerRequestPayload, options?: any): AxiosPromise<DeploymentStatusResponse> {
            return localVarFp.startMinecraftServerMinecraftServerPost(startServerRequestPayload, options).then((request) => request(axios, basePath));
        },
        /**
         * Stop the server if it is running.  If the `wait_n_minutes_before_destroy` parameter is set, the server will be stopped after the specified amount of time. Otherwise the server will be stopped immediately.
         * @summary Stop Minecraft Server
         * @param {DestroyServer} destroyServer
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        stopMinecraftServerMinecraftServerDelete(destroyServer: DestroyServer, options?: any): AxiosPromise<DeploymentStatusResponse> {
            return localVarFp.stopMinecraftServerMinecraftServerDelete(destroyServer, options).then((request) => request(axios, basePath));
        },
    };
};

/**
 * MinecraftServerApi - object-oriented interface
 * @export
 * @class MinecraftServerApi
 * @extends {BaseAPI}
 */
export class MinecraftServerApi extends BaseAPI {
    /**
     * Describe the current state of the minecraft deployment.  Deployment can be in any of 6 states:  | State | Description | | --- | --- | | `SERVER_OFFLINE` | The `awscdk-minecraft-server` CloudFormation stack does not exist or is in a `DELETE_COMPLETE` state. | | `SERVER_PROVISIONING` | The latest execution of the `provision-minecraft-server` Step Function state machine is in a `RUNNING` state. | | `SERVER_PROVISIONING_FAILED` | The latest execution of the `provision-minecraft-server` Step Function state machine is in a `FAILED` state. | | `SERVER_ONLINE` | The `awscdk-minecraft-server` CloudFormation stack exists and is in a `CREATE_COMPLETE` state. | | `SERVER_DEPROVISIONING` | The latest execution of the `deprovision-minecraft-server` AWS Step Function state machine is in a `RUNNING` state AND the execution does not have a `wait_n_minutes_before_deprovisioning` input parameter. | | `SERVER_DEPROVISIONING_FAILED` | The latest execution of the `deprovision-minecraft-server` AWS Step Function state machine. |  Depending on which `FAILED` state is the most recent, the status will be `SERVER_PROVISIONING_FAILED` or `SERVER_DEPROVISIONING_FAILED`.
     * @summary Get Minecraft Server Deployment Status
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     * @memberof MinecraftServerApi
     */
    public getMinecraftServerDeploymentStatusMinecraftServerStatusGet(options?: AxiosRequestConfig) {
        return MinecraftServerApiFp(this.configuration).getMinecraftServerDeploymentStatusMinecraftServerStatusGet(options).then((request) => request(this.axios, this.basePath));
    }

    /**
     * Get the minecraft server ip address.
     * @summary Get Minecraft Server Ip Address
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     * @memberof MinecraftServerApi
     */
    public getMinecraftServerIpAddressMinecraftServerIpAddressGet(options?: AxiosRequestConfig) {
        return MinecraftServerApiFp(this.configuration).getMinecraftServerIpAddressMinecraftServerIpAddressGet(options).then((request) => request(this.axios, this.basePath));
    }

    /**
     * Start the server if it is not already running.
     * @summary Start Minecraft Server
     * @param {StartServerRequestPayload} startServerRequestPayload
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     * @memberof MinecraftServerApi
     */
    public startMinecraftServerMinecraftServerPost(startServerRequestPayload: StartServerRequestPayload, options?: AxiosRequestConfig) {
        return MinecraftServerApiFp(this.configuration).startMinecraftServerMinecraftServerPost(startServerRequestPayload, options).then((request) => request(this.axios, this.basePath));
    }

    /**
     * Stop the server if it is running.  If the `wait_n_minutes_before_destroy` parameter is set, the server will be stopped after the specified amount of time. Otherwise the server will be stopped immediately.
     * @summary Stop Minecraft Server
     * @param {DestroyServer} destroyServer
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     * @memberof MinecraftServerApi
     */
    public stopMinecraftServerMinecraftServerDelete(destroyServer: DestroyServer, options?: AxiosRequestConfig) {
        return MinecraftServerApiFp(this.configuration).stopMinecraftServerMinecraftServerDelete(destroyServer, options).then((request) => request(this.axios, this.basePath));
    }
}
