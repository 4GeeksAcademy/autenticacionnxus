const getState = ({ getStore, getActions, setStore }) => {
    return {
        store: {
            message: null,
            token: localStorage.getItem("token") || null,
            profile: null,
            demo: [
                {
                    title: "FIRST",
                    background: "white",
                    initial: "white",
                },
                {
                    title: "SECOND",
                    background: "white",
                    initial: "white",
                },
            ],
        },
        actions: {
            getIsLogin: () => {
                return getStore();
            },

            resetLocalStorage: () => {
                const store = getStore();
                localStorage.removeItem("token");
                setStore({ ...store, token: null, profile: null });
            },

            loginUser: async ({ email, password }) => {
                try {
                    const resp = await fetch(`${process.env.BACKEND_URL}/api/token`, {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                        },
                        body: JSON.stringify({ email, password }),
                    });

                    // Asegúrate de que la respuesta sea válida
                    if (!resp.ok) {
                        const errorData = await resp.json();
                        throw new Error(errorData.message || 'Error al iniciar sesión.');
                    }

                    const data = await resp.json();
                    setStore({ token: data.token });
                    localStorage.setItem("token", data.token);
                    await getActions().getUserProfile();
                    return data.authorize;
                } catch (error) {
                    console.error("Error loading message from backend", error);
                }
            },

            getUserProfile: async () => {
                const store = getStore();
                try {
                    const resp = await fetch(`${process.env.BACKEND_URL}/api/profile/user`, {
                        method: "GET",
                        headers: {
                            "Content-Type": "application/json",
                            Authorization: "Bearer " + store.token,
                        },
                    });
                    if (resp.ok) {
                        const data = await resp.json();
                        setStore({ profile: data });
                        return true;
                    }
                    console.log("Token expired");
                    return false;
                } catch (error) {
                    console.error("Error loading message from backend", error);
                    return false;
                }
            },

            createUser: async (user) => {
                try {
                    const resp = await fetch(`${process.env.BACKEND_URL}/api/register`, {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                        },
                        body: JSON.stringify(user),
                    });
                    if (!resp.ok) {
                        const errorData = await resp.json();
                        throw new Error(errorData.message || 'Error al crear el usuario.');
                    }
                    return true;
                } catch (err) {
                    console.error("Error sending customer to backend", err);
                }
            },

            logOut: () => {
                localStorage.removeItem("token");
                setStore({ token: null, profile: null });
            },
        },
    };
};

export default getState;
