import { Component, inject } from '@angular/core';
import { ActivatedRoute, NavigationEnd, Router, RouterOutlet } from '@angular/router';
import { LoggerService } from '../../core/services/logger.service';
import { filter } from 'rxjs';
import { BudgetConfiguration } from '../../core/models/budget.model';

interface Tab {
    name: string;
    value: string;
}

@Component({
    selector: 'app-budgets-page',
    standalone: true,
    imports: [RouterOutlet],
    templateUrl: './budgets-page.component.html',
    styleUrl: './budgets-page.component.css'
})
export class BudgetsPageComponent {
    private logger = inject(LoggerService);
    private router = inject(Router);
    private route = inject(ActivatedRoute);

    moduleId = Number(this.route.snapshot.paramMap.get('id'));
    moduleData: BudgetConfiguration | null = null;
    isLoading = true;

    currentTab = 'summary';
    tabs: Tab[] = [
        {
            name: 'Summary',
            value: 'summary'
        },
        {
            name: 'Purchases',
            value: 'purchases'
        },
        {
            name: 'Settings',
            value: 'settings'
        }
    ]

    ngOnInit(): void {
        // Subscribe to navigation events to keep track of the current tab
        this.router.events
            .pipe(filter(event => event instanceof NavigationEnd))
            .subscribe(() => {
                const childRoute = this.route.firstChild;
                if (childRoute?.snapshot?.url?.[0]) {
                    this.currentTab = childRoute.snapshot.url[0].path;
                }
            });

        const initialChild = this.route.firstChild?.snapshot?.url?.[0]?.path;
        if (initialChild) {
            this.currentTab = initialChild;
        }
    }

    onTabChange(tab: string) {
        this.currentTab = tab;
        this.router.navigate([tab], { relativeTo: this.route });
    }

    getSelectedTab(event: Event) {
        return (event.target as HTMLSelectElement).value;
    }
}
