import { Component, inject } from '@angular/core';
import { BudgetConfiguration, BudgetPurchase } from '@core/models/budget.model';
import { BudgetService } from '@core/services/budget.service';
import { LoggerService } from '@core/services/logger.service';
import { NgIcon, provideIcons } from '@ng-icons/core';
import {
    ionAdd,
    ionClose,
    ionPencil,
    ionTrashBin
} from '@ng-icons/ionicons';
import { CommonModule } from '@angular/common';
import { ToastService } from '@shared/ui/toast/toast.service';
import { ModalComponent } from '@layout/modal/modal.component';
import { FormsModule } from '@angular/forms';
import { SpinningIconComponent } from "@shared/icons/spinning-icon/spinning-icon.component";
import { ActivatedRoute, Router } from '@angular/router';

@Component({
    selector: 'app-budget-purchases-tab',
    standalone: true,
    imports: [NgIcon, CommonModule, ModalComponent, FormsModule, SpinningIconComponent],
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
    private route = inject(ActivatedRoute);
    private router = inject(Router);
    private budgetService = inject(BudgetService);
    private toastService = inject(ToastService);
    private logger = inject(LoggerService);

    budgetId = Number(this.route.parent?.snapshot.paramMap.get('id'));
    budgetConfiguration: BudgetConfiguration | null = null;

    isLoading = true;
    purchases: BudgetPurchase[] = [];

    showAddMenu = false;

    // Add/edit purchase
    isSetPurchaseModalOpen = false;
    setPurchaseForm: BudgetPurchase = {
        id: undefined,
        purchase_date: new Date(),
        amount: 0,
        description: '',
        category: null
    }

    // Bulk add purchases
    isBulkImportModalOpen = false;
    bulkRawInput = '';
    bulkParsedHeaders: string[] = [];
    bulkFieldMapping: (keyof BudgetPurchase | '')[] = [];
    bulkPreviewRows: { values: string[]; category: number | null }[] = [];
    bulkInvertPrice = false;
    isParsing = false;

    ngOnInit(): void {
        this.isLoading = true;
        // Get budget details from API
        this.budgetService.getBudgetConfiguration(this.budgetId).subscribe({
            next: (res) => {
                this.budgetConfiguration = res;
                this.isLoading = false;
            },
            error: (error) => {
                this.isLoading = false;
                this.logger.error('Error fetching budget details', error);
                this.toastService.show('Error fetching budget details', 'error', 3000);
                this.router.navigate(['/modules']);
            }
        })

        // Get purchase history from API
        this.budgetService.getPurchases(this.budgetId, { get_all: true }).subscribe({
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
    }

    onAddOption(option: 'single' | 'bulk' | 'import') {
        this.showAddMenu = false;
        if (option === 'single') {
            this.openSetPurchaseModal();
        } else if (option === 'bulk') {
            this.openBulkPurchaseModal();
        } else if (option === 'import') {
            this.openImportModal();
        }
    }

    openBulkPurchaseModal() {
        this.isBulkImportModalOpen = true;
        this.bulkRawInput = '';
        this.bulkParsedHeaders = [];
        this.bulkFieldMapping = [];
        this.bulkPreviewRows = [];
        this.bulkInvertPrice = false;
    }

    openImportModal() {
        this.toastService.show('Not implemented yet', 'error', 3000);
    }

    openSetPurchaseModal(purchase?: BudgetPurchase) {
        this.isSetPurchaseModalOpen = true;

        if (purchase) {
            this.setPurchaseForm = { ...purchase };
        } else {
            this.setPurchaseForm = {
                id: undefined,
                purchase_date: new Date(),
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
            this.budgetService.updatePurchase(this.budgetConfiguration!.id, this.setPurchaseForm.id, this.setPurchaseForm).subscribe({
                next: (res) => {
                    this.purchases = this.purchases.map(p => p.id === res.id ? res : p);
                    this.purchases.sort((a, b) => b.purchase_date.getTime() - a.purchase_date.getTime());
                    this.closeSetPurchaseModal();
                },
                error: (error) => {
                    this.logger.error('Error updating purchase', error);
                    this.toastService.show('Error updating purchase', 'error', 3000);
                }
            });
        } else {
            this.budgetService.addPurchase(this.budgetConfiguration!.id, this.setPurchaseForm).subscribe({
                next: (res) => {
                    this.purchases.push(res);
                    this.purchases.sort((a, b) => b.purchase_date.getTime() - a.purchase_date.getTime());
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
        this.budgetService.deletePurchase(this.budgetConfiguration!.id, purchaseId).subscribe({
            next: () => {
                this.purchases = this.purchases.filter(f => f.id !== purchaseId);
            },
            error: (error) => {
                this.logger.error('Error deleting purchase', error);
                this.toastService.show('Error deleting purchase', 'error', 3000);
            }
        });
    }

    onParseBulkInput() {
        this.isParsing = true;
        const lines = this.bulkRawInput.trim().split(/\r?\n/);
        const rows = lines.map(line => line.split(/\t+/));

        if (!rows.length) return;

        // Detect if the first row is a header
        const hasHeader = rows[0].every(col => isNaN(Number(col)));

        const dataRows = hasHeader ? rows.slice(1) : rows;
        this.bulkParsedHeaders = hasHeader ? rows[0] : rows[0].map((_, i) => `Column ${i + 1}`);

        // Try to auto-detect field mapping
        this.bulkFieldMapping = this.bulkParsedHeaders.map(header => {
            const lower = header.toLowerCase();
            if (hasHeader && (lower.includes('desc') || lower.includes('details'))) return 'description';
            if ((hasHeader && lower.includes('date')) || (!isNaN((new Date(header)).getTime()))) return 'purchase_date';
            if (
                (hasHeader && (
                    lower.includes('amount')
                    || lower.includes('amt')
                    || lower.includes('price')
                    || lower.includes('cost')))
                || !isNaN(Number(header.replace(/[\$,]/g, '').trim()))) return 'amount';
            return '';
        });

        this.bulkPreviewRows = dataRows.map(row => ({
            values: row,
            category: null
        }));

        this.isParsing = false;
    }

    removeBulkRow(index: number) {
        this.bulkPreviewRows.splice(index, 1);
    }

    parseFlexibleDate(input: string): Date | null {
        const formats = [
            { regex: /^(\d{4})[-\/](\d{1,2})[-\/](\d{1,2})$/, order: ['year', 'month', 'day'] }, // yyyy-mm-dd or yyyy/mm/dd
            { regex: /^(\d{1,2})[\/-](\d{1,2})[\/-](\d{4})$/, order: ['day', 'month', 'year'] }, // dd/mm/yyyy or dd-mm-yyyy
            { regex: /^(\d{1,2})[\/-](\d{1,2})[\/-](\d{2})$/, order: ['day', 'month', 'yearShort'] } // dd/mm/yy or dd-mm-yy
        ];

        for (const fmt of formats) {
            const match = input.trim().match(fmt.regex);
            if (!match) continue;

            const parts: Record<string, number> = {};
            fmt.order.forEach((part, i) => {
                let val = parseInt(match[i + 1], 10);
                if (part === 'yearShort') val += val < 50 ? 2000 : 1900;
                parts[part.replace('Short', '')] = val;
            });

            // JS months are 0-indexed
            const date = new Date(parts['year'], parts['month'] - 1, parts['day']);
            if (!isNaN(date.getTime())) {
                return date;
            }
        }

        return null;
    }

    saveBulkImport() {
        // Ensure required fields are mapped
        const requiredFields: (keyof BudgetPurchase)[] = ['purchase_date', 'amount', 'description'];

        const fieldCounts: Record<string, number> = {};
        for (const field of this.bulkFieldMapping) {
            if (field === '') continue;
            fieldCounts[field] = (fieldCounts[field] || 0) + 1;
        }

        // Check for missing or duplicate mappings
        for (const key of requiredFields) {
            const count = fieldCounts[key] || 0;
            if (count === 0) {
                this.toastService.show(`Missing mapping for ${key}`, 'error', 5000);
                return;
            }
            if (count > 1) {
                this.toastService.show(`Field type "${key}" is mapped more than once. Each field must be unique.`, 'error', 5000);
                return;
            }
        }
        // Get column indexes
        const purchaseDateIndex = this.bulkFieldMapping.indexOf('purchase_date');
        const amountIndex = this.bulkFieldMapping.indexOf('amount');
        const descriptionIndex = this.bulkFieldMapping.indexOf('description');

        if (purchaseDateIndex === -1 || amountIndex === -1 || descriptionIndex === -1) {
            this.toastService.show('All field types must be mapped before importing.', 'error', 3000);
            return;
        }

        const result: BudgetPurchase[] = this.bulkPreviewRows.map((row, i) => {
            // Validate dates are in the correct format
            const rawDate = row.values[purchaseDateIndex];
            const parsedDate = this.parseFlexibleDate(rawDate);

            if (!parsedDate) {
                this.toastService.show(`Invalid date format in row ${i + 1}`, 'error', 3000);
                throw new Error('Invalid date format');
            }

            const amount = parseFloat(row.values[amountIndex].replace(/[\$,]/g, '') || '0');

            return {
                purchase_date: parsedDate,
                amount: this.bulkInvertPrice ? -amount : amount,
                description: row.values[descriptionIndex],
                category: row.category ?? null
            };
        });

        console.log('Imported purchases:', result);

        this.budgetService.addBulkPurchase(this.budgetConfiguration!.id, result).subscribe({
            next: (res) => {
                this.toastService.show(`Imported ${res.length} purchases`, 'success', 3000);
                this.purchases.push(...res);
                this.isBulkImportModalOpen = false;
            },
            error: (error) => {
                this.toastService.show('Error importing purchases', 'error', 3000);
                this.logger.error('Error importing purchases', error);
            }
        })
    }

    parseDate(date: string | null): Date {
        if (!date) {
            this.toastService.show('Date is required', 'error', 3000);
            throw new Error('Date is required');
        }

        const parsedDate = new Date(date);
        if (isNaN(parsedDate.getTime())) {
            this.toastService.show('Invalid date format', 'error', 3000);
            throw new Error('Invalid date format');
        }
        return parsedDate;
    }
}
