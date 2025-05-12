import { Component, inject } from '@angular/core';
import { ActivatedRoute, Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { LoggerService } from '../../core/services/logger.service';

@Component({
    selector: 'app-budgets-page',
    standalone: true,
    imports: [RouterOutlet, RouterLink, RouterLinkActive],
    templateUrl: './budgets-page.component.html',
    styleUrl: './budgets-page.component.css'
})
export class BudgetsPageComponent {
    private logger = inject(LoggerService);
    private router = inject(Router);
    private route = inject(ActivatedRoute);

    currentTab = 'summary';

    onTabChange(event: Event) {
        const selectedTab = (event.target as HTMLSelectElement).value;
        this.currentTab = selectedTab;
        this.router.navigate([selectedTab], { relativeTo: this.route });
    }
}
