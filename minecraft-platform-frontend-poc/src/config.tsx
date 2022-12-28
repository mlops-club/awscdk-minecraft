import axios from "axios"

/**
 * Static configuration values for the frontend.
 *
 * Most of these values are necessary in order to correctly interact with
 * external services such as the backend API and AWS Cognito.
 */
export type MinecraftFrontendConfig = {

    /**
     * Base URL for the backend API.
     */
    readonly backend_api_url: string

    /**
     * AWS Cognito configuration values.
     */
    readonly cognito_user_pool_id: string
    readonly cognito_hosted_ui_app_client_id: string
    readonly cognito_hosted_ui_app_client_allowed_scopes: Array<string>
    readonly cognito_hosted_ui_fqdn: string
    readonly cognito_user_pool_region: string

    /**
     * URL to redirect to after a successful sign-in. This URL must be registered
     * with the cognito app client in advance.
     */
    readonly cognito_hosted_ui_redirect_sign_in_url: string

    /**
     * URL to redirect to after a successful sign-out. This URL must be registered
     * with the cognito app client in advance.
     */
    readonly cognito_hosted_ui_redirect_sign_out_url: string
}

/**
 * Fetch the global application config from the config.json file.
 *
 * These configuration values point to things like the backend API URL,
 * and information about any AWS resources needed by the frontend.
 */
export const fetchConfig = async (): Promise<MinecraftFrontendConfig> => {
    const url = isLocalhost() ? '/static/config.dev.json' : "/static/config.json";
    console.log("is localhost", isLocalhost(), url)
    const response: { data: MinecraftFrontendConfig } = await axios.get(url);
    return response.data;
}

/**
 * Determine whether the window URL is localhost.
 * If not, we assume we are running in production.
 */
const isLocalhost = () => Boolean(
    window.location.hostname === "localhost" ||
    // [::1] is the IPv6 localhost address.
    window.location.hostname === "[::1]" ||
    // 127.0.0.1/8 is considered localhost for IPv4.
    window.location.hostname.match(
        /^127(?:\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}$/
    )
);
