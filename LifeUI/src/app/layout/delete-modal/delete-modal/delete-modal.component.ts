import { Component, input, output } from '@angular/core';
import { ModalComponent } from '@layout/modal/modal.component';

@Component({
    selector: 'app-delete-modal',
    standalone: true,
    imports: [ModalComponent],
    templateUrl: './delete-modal.component.html',
    styleUrl: './delete-modal.component.css',
})
export class DeleteModalComponent {
    show = input<boolean>(false);
    message = input<string>(
        'Are you sure you want to delete this item? This action cannot be undone.'
    );
    title = input<string>('Delete Item');

    onCancel = output<void>();
    onDelete = output<void>();

    handleCancel() {
        this.onCancel.emit();
    }

    handleDelete() {
        this.onDelete.emit();
    }
}
