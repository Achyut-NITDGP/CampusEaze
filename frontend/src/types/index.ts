export type Role = "user" | "owner" | "manager" | "admin";
export type Row = Record<string, any>;
export interface User { id: number; name: string; email: string; role: Role; verification_status: string; active: boolean }
export interface Resource { id: number; owner_id: number; name: string; category: string; location: string; price_per_hour: number; photo_url: string | null; required_qualification: string | null; [k: string]: any }
export interface Booking { id: number; resource_id: number; user_id: number; start_time: string; end_time: string; purpose: string; status: string; amount: number; payment_status: string; resource_name: string; user_name: string; waitlist_position: number | null; has_conflict: boolean; [k: string]: any }
