import { Component, inject } from '@angular/core';
import { ActivatedRoute, Router, RouterOutlet } from '@angular/router';
import { LoggerService } from '../../core/services/logger.service';

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

    currentTab = 'summary';

    tabs = [
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

    onTabChange(tab: string) {
        this.currentTab = tab;
        this.router.navigate([tab], { relativeTo: this.route });
    }

    getSelectedTab(event: Event) {
        return (event.target as HTMLSelectElement).value;
    }
}
