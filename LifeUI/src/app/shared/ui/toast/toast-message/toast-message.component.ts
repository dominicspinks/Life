import { Component, input, inject, OnInit } from '@angular/core';
import { NgIcon, provideIcons } from '@ng-icons/core';
import { ionClose } from '@ng-icons/ionicons';
import { ToastService } from '../toast.service';

@Component({
    selector: 'app-toast-message',
    standalone: true,
    imports: [NgIcon],
    providers: [provideIcons({ ionClose })],
    templateUrl: './toast-message.component.html'
})
export class ToastMessageComponent implements OnInit {
    id = input.required<number>();
    type = input<'success' | 'error' | 'warning' | 'info'>('info');
    message = input<string>('');
    duration = input<number>(0);

    private toastService = inject(ToastService);

    progress = 100;
    intervalId?: any;

    ngOnInit(): void {
        if (this.duration() > 0) {
            const total = this.duration();
            const start = Date.now();

            this.intervalId = setInterval(() => {
                const elapsed = Date.now() - start;
                const percent = Math.max(0, 100 - (elapsed / total) * 100);
                this.progress = percent;

                if (percent <= 0) {
                    clearInterval(this.intervalId);
                }
            }, 100);
        }
    }

    close(): void {
        this.toastService.dismiss(this.id());
        if (this.intervalId) clearInterval(this.intervalId);
    }

    get bgClass(): string {
        const t = this.type();
        return {
            success: 'bg-green-500 text-white',
            error: 'bg-red-500 text-white',
            warning: 'bg-yellow-500 text-black',
            info: 'bg-blue-500 text-white',
        }[t]!;
    }
}
