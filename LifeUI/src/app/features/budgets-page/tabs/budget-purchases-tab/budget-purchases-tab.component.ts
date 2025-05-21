import { Component, inject } from '@angular/core';
import { BudgetContextService } from '../../../../core/contexts/BudgetContext.service';
import { BudgetConfiguration, BudgetPurchase } from '../../../../core/models/budget.model';
import { BudgetService } from '../../../../core/services/budget.service';
import { LoggerService } from '../../../../core/services/logger.service';
import { NgIcon, provideIcons } from '@ng-icons/core';
import {
    ionAdd,
    ionClose,
    ionPencil,
    ionTrashBin
} from '@ng-icons/ionicons';
import { CommonModule } from '@angular/common';
import { ToastService } from '../../../../shared/ui/toast/toast.service';
import { ModalComponent } from '../../../../layout/modal/modal.component';
import { FormsModule } from '@angular/forms';

@Component({
    selector: 'app-budget-purchases-tab',
    standalone: true,
    imports: [NgIcon, CommonModule, ModalComponent, FormsModule],
    providers: [provideIcons({
        ionAdd,
        ionClose,
        ionPencil,
        ionTrashBin
    })],
    templateUrl: './budget-purchases-tab.component.html',
    styleUrl: './budget-purchases-tab.component.css'
})
export class BudgetPurchasesTabComponent {
    private budgetContext = inject(BudgetContextService);
    private budgetService = inject(BudgetService);
    private toastService = inject(ToastService);
    private logger = inject(LoggerService);

    isLoading = true;
    budgetConfiguration: BudgetConfiguration | null = null;
    purchases: BudgetPurchase[] = [];
    isSetPurchaseModalOpen = false;
    setPurchaseForm: BudgetPurchase = {
        id: undefined,
        purchase_date: new Date().toISOString().split('T')[0],
        amount: 0,
        description: '',
        category: null
    }

    ngOnInit(): void {
        this.isLoading = true;
        this.budgetContext.moduleData$.subscribe(module => {
            if (!module) return;

            this.budgetConfiguration = module;
            this.isLoading = false;

            this.isLoading = true;
            this.budgetService.getBudgetPurchases(this.budgetConfiguration!.id, { get_all: true }).subscribe({
                next: (res) => {
                    this.purchases = res;
                    this.isLoading = false;
                },
                error: (error) => {
                    this.logger.error('Error fetching budget purchases', error);
                    this.toastService.show('Error fetching budget purchases', 'error', 3000);
                    this.isLoading = false;
                }
            })
        });
    }

    openSetPurchaseModal(purchase?: BudgetPurchase) {
        this.isSetPurchaseModalOpen = true;

        if (purchase) {
            this.setPurchaseForm = { ...purchase };
        } else {
            this.setPurchaseForm = {
                id: undefined,
                purchase_date: new Date().toISOString().split('T')[0],
                amount: 0,
                description: '',
                category: null
            }
        }
    }

    closeSetPurchaseModal() {
        this.isSetPurchaseModalOpen = false;
    }

    saveSetPurchase() {
        // Validate the form
        // Validate mandatory fields are filled
        if (!this.setPurchaseForm.purchase_date || !this.setPurchaseForm.amount || !this.setPurchaseForm.description) {
            this.toastService.show('Fill all mandatory fields', 'error', 3000);
            return;
        }

        // Validate category exists (if selected)
        if (this.setPurchaseForm.category) {
            const category = this.budgetConfiguration!.categories.find(f => f.id === this.setPurchaseForm.category);
            if (!category) {
                this.toastService.show('Invalid category', 'error', 3000);
                return;
            }
        }

        if (this.setPurchaseForm.id) {
            this.budgetService.updateBudgetPurchase(this.budgetConfiguration!.id, this.setPurchaseForm.id, this.setPurchaseForm).subscribe({
                next: (res) => {
                    this.purchases = this.purchases.map(p => p.id === res.id ? res : p);
                    this.closeSetPurchaseModal();
                },
                error: (error) => {
                    this.logger.error('Error updating purchase', error);
                    this.toastService.show('Error updating purchase', 'error', 3000);
                }
            });
        } else {
            this.budgetService.addBudgetPurchase(this.budgetConfiguration!.id, this.setPurchaseForm).subscribe({
                next: (res) => {
                    this.purchases.push(res);
                    this.closeSetPurchaseModal();
                },
                error: (error) => {
                    this.logger.error('Error adding purchase', error);
                    this.toastService.show('Error adding purchase', 'error', 3000);
                }
            });
        }
    }

    confirmDeletePurchase(purchaseId: number): void {
        const confirmed = confirm('Are you sure you want to delete this purchase?');
        if (confirmed) {
            this.deletePurchase(purchaseId);
        }
    }

    deletePurchase(purchaseId: number): void {
        this.budgetService.deleteBudgetPurchase(this.budgetConfiguration!.id, purchaseId).subscribe({
            next: () => {
                this.purchases.filter(f => f.id !== purchaseId);
            },
            error: (error) => {
                this.logger.error('Error deleting purchase', error);
                this.toastService.show('Error deleting purchase', 'error', 3000);
            }
        });
    }
}
