import { Booking, Row } from "../types";
import { api } from "./api";

export const create = (body: Row) => api<Booking>("/bookings", { body });
export const decide = (id: number, decision: string, reason: string) => api(`/bookings/${id}/decision`, { body: { decision, reason } });
export const cancel = (id: number) => api(`/bookings/${id}/cancel`, { body: {} });
