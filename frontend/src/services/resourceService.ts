import { Row } from "../types";
import { api } from "./api";

export const save = (id: string | undefined, body: Row) => (id ? api(`/resources/${id}`, { method: "PUT", body }) : api("/resources", { body }));
export const block = (id: string, body: Row) => api(`/resources/${id}/blocks`, { body });
