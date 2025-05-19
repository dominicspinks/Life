import { Injectable } from "@angular/core";
import { BehaviorSubject } from "rxjs";
import { BudgetConfiguration } from "../models/budget.model";

@Injectable({ providedIn: 'root' })
export class BudgetContextService {
    private moduleDataSubject = new BehaviorSubject<BudgetConfiguration | null>(null);
    moduleData$ = this.moduleDataSubject.asObservable();

    setModuleData(data: BudgetConfiguration | null) {
        this.moduleDataSubject.next(data);
    }

    getModuleData(): BudgetConfiguration | null {
        return this.moduleDataSubject.value;
    }
}
