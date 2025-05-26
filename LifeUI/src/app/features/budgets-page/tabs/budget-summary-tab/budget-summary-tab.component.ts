import { Component, inject } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { BudgetService } from '@core/services/budget.service';
import { LoggerService } from '@core/services/logger.service';
import { ToastService } from '@shared/ui/toast/toast.service';
import { BudgetConfiguration, BudgetPurchaseSummary } from '@core/models/budget.model';
import { CurrencyPipe, NgClass } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { SpinningIconComponent } from '@shared/icons/spinning-icon/spinning-icon.component';

@Component({
    selector: 'app-budget-summary-tab',
    standalone: true,
    imports: [CurrencyPipe, FormsModule, SpinningIconComponent, NgClass],
    templateUrl: './budget-summary-tab.component.html',
    styleUrl: './budget-summary-tab.component.css'
})
export class BudgetSummaryTabComponent {
    private route = inject(ActivatedRoute);
    private router = inject(Router);
    private budgetService = inject(BudgetService);
    private toastService = inject(ToastService);
    private logger = inject(LoggerService);

    budgetId = Number(this.route.parent?.snapshot.paramMap.get('id'));
    budgetConfiguration: BudgetConfiguration | null = null;
    isLoading = true;
    activeYear: number = new Date().getFullYear();
    activeWeek: number = this.getActiveWeek();

    budgetYears: number[] = [];

    showBreakdown = false;
    weeklySummary: BudgetPurchaseSummary[] = [];
    weeks: number[] = Array.from({ length: 53 }, (_, i) => i + 1);

    statusColours: Record<'ok' | 'warning' | 'bad', string> = {
        ok: 'text-green-950 bg-green-100',
        warning: 'text-yellow-950 bg-yellow-100',
        bad: 'text-red-950 bg-red-100'
    };

    ngOnInit() {
        this.isLoading = true;
        // Get budget details from API
        this.budgetService.getBudgetConfiguration(this.budgetId).subscribe({
            next: (res) => {
                this.budgetConfiguration = res;
            },
            error: (error) => {
                this.isLoading = false;
                this.logger.error('Error fetching budget details', error);
                this.toastService.show('Error fetching budget details', 'error', 3000);
                this.router.navigate(['/modules']);
            }
        })

        // Get budget years from API
        this.budgetService.getBudgetYears(this.budgetId).subscribe({
            next: (res) => {
                this.budgetYears = res;
                // Add current year if missing from response
                if (!this.budgetYears.includes(this.activeYear)) {
                    this.budgetYears.push(this.activeYear);
                    this.budgetYears.sort((a, b) => b - a);
                }
                this.loadSummaryData();
            },
            error: (error) => {
                this.isLoading = false;
                this.logger.error('Error fetching budget years', error);
                this.toastService.show('Error fetching budget years', 'error', 3000);
            }
        })
    }

    get orderedCategories() {
        return this.budgetConfiguration?.categories
            .slice()
            .filter(c => c.is_enabled)
            .sort((a, b) => a.order - b.order) ?? [];
    }

    getTotal(week: number, categoryId: number): number | null {
        return this.weeklySummary.find(w => w.week === week && w.category === categoryId)?.total ?? null;
    }

    getWeekTotal(week: number): number {
        return this.weeklySummary
            .filter(row => row.week === week)
            .reduce((sum, row) => sum + row.total, 0);
    }

    onYearChange(year: number): void {
        this.activeYear = year;
        this.loadSummaryData();
    }

    loadSummaryData(): void {
        this.isLoading = true;
        const start = `${this.activeYear}-01-01`;
        const end = `${this.activeYear + 1}-01-01`;

        this.budgetService.getPurchaseSummary(this.budgetId, start, end).subscribe({
            next: (res) => {
                this.weeklySummary = res;
                this.isLoading = false;
                this.logger.info('Weekly summary fetched', res);
            },
            error: (error) => {
                this.logger.error('Error fetching summary data', error);
                this.toastService.show('Error fetching details', 'error', 3000);
                this.isLoading = false;
            }
        });
    }

    get summaryRows(): { name: string; values: Record<number, number> }[] {
        const categories = this.orderedCategories;
        const dataByCategory: Record<number, number[]> = {};
        const result: { name: string; values: Record<number, number> }[] = [];

        // Group data by category
        for (const entry of this.weeklySummary) {
            if (!dataByCategory[entry.category]) dataByCategory[entry.category] = [];
            dataByCategory[entry.category].push(entry.total);
        }

        const latestWeek = Math.max(...this.weeklySummary.map(w => w.week), 1);

        const totals: Record<number, number> = {};
        const averages: Record<number, number> = {};
        const targets: Record<number, number> = {};
        const variances: Record<number, number> = {};

        for (const category of categories) {
            const data = dataByCategory[category.id!] || [];
            const total = data.reduce((sum, value) => sum + value, 0);
            const average = latestWeek ? total / (latestWeek) : 0;
            const target = category.weekly_target;
            const variance = total - target * latestWeek;

            totals[category.id!] = total;
            averages[category.id!] = average;
            targets[category.id!] = target;
            variances[category.id!] = variance;
        }

        // Compute total column (id: 0) by excluding excluded_from_budget categories
        const includedCategories = categories.filter(c => !c.excluded_from_budget);

        totals[0] = includedCategories.reduce((sum, c) => sum + (totals[c.id!] || 0), 0);
        averages[0] = includedCategories.reduce((sum, c) => sum + (averages[c.id!] || 0), 0);
        targets[0] = includedCategories.reduce((sum, c) => sum + (targets[c.id!] || 0), 0);
        variances[0] = includedCategories.reduce((sum, c) => sum + (variances[c.id!] || 0), 0);

        result.push({ name: 'Total', values: totals });
        result.push({ name: 'Average', values: averages });
        result.push({ name: 'Weekly Target', values: targets });
        result.push({ name: 'Variance', values: variances });

        return result;
    }

    getCellColour(week: number, categoryId: number): string {
        let value: number;
        let target: number;

        if (categoryId === 0) {
            const included = this.orderedCategories.filter(c => !c.excluded_from_budget);
            value = this.getWeekTotal(week);
            target = included.reduce((sum, c) => sum + c.weekly_target, 0);
        } else {
            const category = this.orderedCategories.find(c => c.id === categoryId);
            if (!category) return '';
            value = this.getTotal(week, categoryId) ?? 0;
            target = category.weekly_target;
        }

        if (value < target) return this.statusColours.ok;
        if (value < 2 * target) return this.statusColours.warning;
        return this.statusColours.bad;
    }

    getAverageCellColour(categoryId: number): string {
        if (categoryId === 0) {
            // For totals column: calculate target = sum of included targets
            const included = this.orderedCategories.filter(c => !c.excluded_from_budget);
            const target = included.reduce((sum, c) => sum + c.weekly_target, 0);
            const average = this.summaryRows.find(r => r.name === 'Average')?.values[0] ?? 0;

            if (average < target) return this.statusColours.ok;
            if (average > 1.2 * target) return this.statusColours.warning;
            return this.statusColours.bad;
        }

        const category = this.orderedCategories.find(c => c.id === categoryId);
        if (!category) return '';

        const average = this.summaryRows.find(r => r.name === 'Average')?.values[categoryId] ?? 0;

        if (average < category.weekly_target) return this.statusColours.ok;
        if (average < 1.2 * category.weekly_target) return this.statusColours.warning;
        return this.statusColours.bad;
    }

    isCurrentWeek(week: number): boolean {
        return week === this.activeWeek;
    }

    getActiveWeek() {
        const dt = new Date();
        const ys = new Date(dt.getFullYear(), 0, 1);
        const dp = (dt.getTime() - ys.getTime()) / 86400000;
        const sw = ys.getDay();
        const so = (sw === 0) ? 6 : sw - 1;
        const wn = Math.floor((dp + so) / 7);
        this.logger.info('Week number', [dt, ys, dp, sw, so, wn]);

        return wn;
    }

    getVarianceCellColour(categoryId: number): string {
        const variance = this.summaryRows.find(r => r.name === 'Variance')?.values[categoryId] ?? 0;
        const target = this.summaryRows.find(r => r.name === 'Weekly Target')?.values[categoryId] ?? 0;

        if (variance <= 0) return this.statusColours.ok;
        if (variance < 0.2 * target * this.activeWeek) return this.statusColours.warning;

        return this.statusColours.bad;
    }
}
