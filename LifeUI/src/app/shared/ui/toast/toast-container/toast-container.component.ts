import { Component, inject } from '@angular/core';
import { ToastService } from '../toast.service';
import { ToastMessageComponent } from '../toast-message/toast-message.component';

@Component({
    selector: 'app-toast-container',
    standalone: true,
    imports: [ToastMessageComponent],
    templateUrl: './toast-container.component.html'
})
export class ToastContainerComponent {
    toastService = inject(ToastService);
}
