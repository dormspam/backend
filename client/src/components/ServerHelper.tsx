export enum ServerURL {
  login = "/api/v1/client/login",
  getAllEvents = "/api/v1/events/all",
  getEvents = "/api/v1/events",
  getEvent = "/api/v1/events/event",
  publishEvent = "/api/v1/events/publish",
  approveEvent = "/api/v1/events/approve",
}

const ServerHelper = {
  post: async (
    url: ServerURL,
    data: any,
  ): Promise<{ success: boolean; [key: string]: any }> => {
    try {
      const config = {
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
      };
      const response = await fetch(url, config);
      if (response.ok) {
        const json = await response.json();
        return json;
      }
    } catch (error) {}
    return { success: false };
  }
};

export default ServerHelper;
