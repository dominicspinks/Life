import { Injectable, signal } from '@angular/core';

export interface ToastMessage {
    id: number;
    message: string;
    type: 'success' | 'error' | 'warning' | 'info';
    duration: number;
}

@Injectable({ providedIn: 'root' })
export class ToastService {
    private counter = 0;
    private _messages = signal<ToastMessage[]>([]);

    messages = this._messages.asReadonly();

    show(message: string, type: ToastMessage['type'] = 'info', duration = 0): void {
        const id = this.counter++;
        const toast: ToastMessage = { id, message, type, duration };
        this._messages.update(msgs => [...msgs, toast]);
        if (duration > 0) {
            setTimeout(() => this.dismiss(id), duration);
        }
    }

    dismiss(id: number): void {
        this._messages.update(msgs => msgs.filter(msg => msg.id !== id));
    }

    clear(): void {
        this._messages.set([]);
    }
}
