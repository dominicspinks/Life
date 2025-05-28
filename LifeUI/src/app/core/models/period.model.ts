export type PeriodName = "daily" | "weekly" | "monthly" | "yearly";

export interface Period {
    id: number;
    name: PeriodName;
}