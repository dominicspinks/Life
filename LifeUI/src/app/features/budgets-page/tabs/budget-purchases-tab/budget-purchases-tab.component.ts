import {
    Component,
    ElementRef,
    HostListener,
    inject,
    ViewChild,
    OnInit,
    OnDestroy,
    AfterViewChecked
} from '@angular/core';
import {
    BudgetConfiguration,
    BudgetDescriptionCategoryRequest,
    BudgetPurchase,
} from '@core/models/budget.model';
import { PaginatedResponse } from '@core/models/pagination.model';
import { BudgetService } from '@core/services/budget.service';
import { LoggerService } from '@core/services/logger.service';
import { Subject } from 'rxjs';
import { debounceTime, distinctUntilChanged } from 'rxjs/operators';
import { NgIcon, provideIcons } from '@ng-icons/core';
import {
    ionAdd,
    ionClose,
    ionPencil,
    ionTrashBin,
    ionSearch,
    ionFilter,
} from '@ng-icons/ionicons';
import { CommonModule } from '@angular/common';
import { ToastService } from '@shared/ui/toast/toast.service';
import { ModalComponent } from '@layout/modal/modal.component';
import { FormsModule } from '@angular/forms';
import { SpinningIconComponent } from '@shared/icons/spinning-icon/spinning-icon.component';
import { ActivatedRoute, Router } from '@angular/router';
import { DeleteModalComponent } from '@layout/delete-modal/delete-modal/delete-modal.component';

@Component({
    selector: 'app-budget-purchases-tab',
    standalone: true,
    imports: [
        NgIcon,
        CommonModule,
        ModalComponent,
        FormsModule,
        SpinningIconComponent,
        DeleteModalComponent,
    ],
    providers: [
        provideIcons({
            ionAdd,
            ionClose,
            ionPencil,
            ionTrashBin,
            ionSearch,
            ionFilter
        }),
    ],
    templateUrl: './budget-purchases-tab.component.html',
    styleUrl: './budget-purchases-tab.component.css',
})
export class BudgetPurchasesTabComponent implements OnInit, OnDestroy, AfterViewChecked {
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

    // Filters and Pagination
    availableYears: number[] = [];
    selectedYear?: number;
    currentPage = 1;
    hasMore = true;
    isLoadingMore = false;
    private needsScrollCheck = false;

    searchQuery = '';
    searchSubject = new Subject<string>();

    showCategoryFilter = false;
    selectedCategories = new Set<number>();
    categorySubject = new Subject<void>();

    @ViewChild('menuWrapper') menuWrapper!: ElementRef;
    @ViewChild('categoryFilterWrapper') categoryFilterWrapper!: ElementRef;

    toggleMenu(event: MouseEvent) {
        event.stopPropagation();
        this.showAddMenu = !this.showAddMenu;
    }
    @HostListener('document:click', ['$event'])
    onClickOutside(event: MouseEvent) {
        if (
            this.showAddMenu &&
            this.menuWrapper &&
            !this.menuWrapper.nativeElement.contains(event.target)
        ) {
            this.showAddMenu = false;
        }
        if (this.showCategoryFilter && this.categoryFilterWrapper && !this.categoryFilterWrapper.nativeElement.contains(event.target)) {
            this.showCategoryFilter = false;
        }
    }

    // Add/edit purchase
    isSetPurchaseModalOpen = false;
    setPurchaseForm: BudgetPurchase = {
        id: undefined,
        purchase_date: new Date(),
        amount: 0,
        description: '',
        category: null,
    };

    // Bulk add purchases
    isBulkImportModalOpen = false;
    bulkRawInput = '';
    bulkParsedHeaders: string[] = [];
    bulkFieldMapping: (keyof BudgetPurchase | '')[] = [];
    bulkPreviewRows: { values: string[]; category: number | null }[] = [];
    bulkInvertPrice = false;
    isParsing = false;

    isSearchingCategories = false;

    showDeleteModal = false;
    deletePurchaseId: number | null = null;

    ngOnInit(): void {
        this.isLoading = true;

        // Set up search debouncing
        this.searchSubject.pipe(
            debounceTime(500),
            distinctUntilChanged()
        ).subscribe(query => {
            this.searchQuery = query;
            this.loadPurchases(true);
        });

        // Set up category debouncing
        this.categorySubject.pipe(
            debounceTime(500)
        ).subscribe(() => {
            this.loadPurchases(true);
        });

        // Get budget details from API
        this.budgetService.getBudgetConfiguration(this.budgetId).subscribe({
            next: (res) => {
                this.budgetConfiguration = res;
                this.budgetConfiguration.categories.filter(c => c.is_enabled).forEach(c => {
                    this.selectedCategories.add(c.id!);
                });

                this.budgetService.getBudgetYears(this.budgetId).subscribe({
                    next: (years) => {
                        this.availableYears = years.sort((a,b) => b - a);
                        const currentYear = new Date().getFullYear();
                        if (!this.availableYears.includes(currentYear)) {
                            this.availableYears.unshift(currentYear);
                        }

                        const savedYear = this.budgetService.getSelectedYear(this.budgetId);
                        this.selectedYear = savedYear ? savedYear : currentYear;

                        this.loadPurchases(true);
                    },
                    error: (error) => {
                        this.logger.error('Error fetching budget years', error);
                        // Fallback to basic load
                        this.loadPurchases(true);
                    }
                });
            },
            error: (error) => {
                this.isLoading = false;
                this.logger.error('Error fetching budget details', error);
                this.toastService.show('Error fetching budget details', 'error', 3000);
                this.router.navigate(['/modules']);
            },
        });
    }

    ngOnDestroy(): void {
        this.searchSubject.complete();
        this.categorySubject.complete();
    }

    ngAfterViewChecked(): void {
        if (this.needsScrollCheck && !this.isLoading && !this.isLoadingMore && this.hasMore) {
            this.needsScrollCheck = false;
            // Use setTimeout to wait for the view to fully render the new rows
            setTimeout(() => {
                const docElement = document.documentElement;
                const hasScrollbar = docElement.scrollHeight > docElement.clientHeight;

                // If there's no vertical scrollbar, auto-fetch the next page to fill the screen
                if (!hasScrollbar && this.hasMore && !this.isLoadingMore) {
                    this.currentPage++;
                    this.loadPurchases(false);
                }
            }, 50);
        }
    }

    onSearchChange(query: string) {
        this.searchSubject.next(query);
    }

    toggleCategoryFilter(event: MouseEvent) {
        event.stopPropagation();
        this.showCategoryFilter = !this.showCategoryFilter;
    }

    onCategoryToggle(categoryId: number) {
        if (this.selectedCategories.has(categoryId)) {
            this.selectedCategories.delete(categoryId);
        } else {
            this.selectedCategories.add(categoryId);
        }
        this.categorySubject.next();
    }

    get allCategoriesSelected(): boolean {
        const enabledCount = this.budgetConfiguration?.categories.filter(c => c.is_enabled).length || 0;
        return this.selectedCategories.size === enabledCount;
    }

    toggleAllCategories() {
        if (this.allCategoriesSelected) {
            this.selectedCategories.clear();
        } else {
            const enabledCategories = this.budgetConfiguration?.categories.filter(c => c.is_enabled) || [];
            enabledCategories.forEach(c => this.selectedCategories.add(c.id!));
        }
        this.categorySubject.next();
    }

    onYearChange(year: string) {
        this.selectedYear = parseInt(year, 10);
        this.budgetService.setSelectedYear(this.budgetId, this.selectedYear);
        this.loadPurchases(true);
    }

    loadPurchases(reset = false) {
        if (reset) {
            this.currentPage = 1;
            this.hasMore = true;
            this.purchases = [];
            this.isLoading = true;
        } else {
            this.isLoadingMore = true;
        }

        if (!this.hasMore && !reset) {
            this.isLoadingMore = false;
            return;
        }

        const enabledCatsCount = this.budgetConfiguration?.categories.filter(c => c.is_enabled).length || 0;
        const sendCategories = this.selectedCategories.size > 0 && this.selectedCategories.size < enabledCatsCount;

        this.budgetService.getPurchases(this.budgetId, {
            page: this.currentPage,
            purchase_date__year: this.selectedYear,
            description: this.searchQuery || undefined,
            category: sendCategories ? Array.from(this.selectedCategories) : undefined,
        }).subscribe({
            next: (res) => {
                const paginated = res as PaginatedResponse<BudgetPurchase>;
                if (reset) {
                    this.purchases = paginated.results;
                } else {
                    this.purchases.push(...paginated.results);
                }
                this.hasMore = !!paginated.next;
                this.isLoading = false;
                this.isLoadingMore = false;

                // Trigger a scrollbar check after view updates
                this.needsScrollCheck = true;
            },
            error: (error) => {
                this.logger.error('Error fetching budget purchases', error);
                this.toastService.show('Error fetching budget purchases', 'error', 3000);
                this.isLoading = false;
                this.isLoadingMore = false;
            }
        });
    }

    @HostListener('window:scroll', ['$event'])
    onWindowScroll() {
        if (this.isLoading || this.isLoadingMore || !this.hasMore) return;

        const pos = (document.documentElement.scrollTop || document.body.scrollTop) + document.documentElement.offsetHeight;
        const max = document.documentElement.scrollHeight;
        if (pos > max - 200) {
            this.currentPage++;
            this.loadPurchases(false);
        }
    }

    onAddOption(option: 'single' | 'bulk' | 'import') {
        this.showAddMenu = false;
        if (option === 'single') {
            this.openSetPurchaseModal();
        } else if (option === 'bulk') {
            this.openBulkPurchaseModal();
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
                category: null,
            };
        }
    }

    closeSetPurchaseModal() {
        this.isSetPurchaseModalOpen = false;
    }

    saveSetPurchase() {
        // Validate the form
        // Validate mandatory fields are filled
        if (
            !this.setPurchaseForm.purchase_date ||
            this.setPurchaseForm.amount == null ||
            isNaN(this.setPurchaseForm.amount) ||
            !this.setPurchaseForm.description
        ) {
            this.toastService.show('Fill all mandatory fields', 'error', 3000);
            return;
        }

        // Validate category exists (if selected)
        if (this.setPurchaseForm.category) {
            const category = this.budgetConfiguration!.categories.find(
                (f) => f.id === this.setPurchaseForm.category
            );
            if (!category) {
                this.toastService.show('Invalid category', 'error', 3000);
                return;
            }
        }

        if (this.setPurchaseForm.id) {
            this.budgetService
                .updatePurchase(
                    this.budgetConfiguration!.id,
                    this.setPurchaseForm.id,
                    this.setPurchaseForm
                )
                .subscribe({
                    next: (res) => {
                        this.purchases = this.purchases.map((p) =>
                            p.id === res.id ? res : p
                        );
                        this.closeSetPurchaseModal();
                    },
                    error: (error) => {
                        this.logger.error('Error updating purchase', error);
                        this.toastService.show(
                            'Error updating purchase',
                            'error',
                            3000
                        );
                    },
                });
        } else {
            this.budgetService
                .addPurchase(this.budgetConfiguration!.id, this.setPurchaseForm)
                .subscribe({
                    next: (res) => {
                        this.loadPurchases(true);
                        this.closeSetPurchaseModal();
                    },
                    error: (error) => {
                        this.logger.error('Error adding purchase', error);
                        this.toastService.show(
                            'Error adding purchase',
                            'error',
                            3000
                        );
                    },
                });
        }
    }

    confirmDeletePurchase(purchaseId: number): void {
        this.showDeleteModal = true;
        this.deletePurchaseId = purchaseId;
    }

    closeDeleteModal() {
        this.showDeleteModal = false;
        this.deletePurchaseId = null;
    }

    deletePurchase(): void {
        if (!this.deletePurchaseId) return;
        this.budgetService
            .deletePurchase(this.budgetConfiguration!.id, this.deletePurchaseId)
            .subscribe({
                next: () => {
                    this.loadPurchases(true);
                    this.closeDeleteModal();
                },
                error: (error) => {
                    this.logger.error('Error deleting purchase', error);
                    this.toastService.show(
                        'Error deleting purchase',
                        'error',
                        3000
                    );
                },
            });
    }

    parseBulkInput() {
        this.isParsing = true;
        const lines = this.bulkRawInput.trim().split(/\r?\n/);
        const rows = lines.map((line) => line.split(/\t+/));

        if (!rows.length) return;

        // Detect if the first row is a header
        const hasHeader = rows[0].every((col) =>
            isNaN(Number(col.replace(/[\$,]/g, '').trim()))
        );
        const dataRows = hasHeader ? rows.slice(1) : rows;
        this.bulkParsedHeaders = rows[0];

        // Try to auto-detect field mapping
        this.bulkFieldMapping = this.bulkParsedHeaders.map((header) => {
            const lower = header.toLowerCase();
            if (
                hasHeader &&
                (lower.includes('desc') || lower.includes('details'))
            )
                return 'description';
            if (
                (hasHeader && lower.includes('date')) ||
                !isNaN(this.parseFlexibleDate(header)?.getTime() ?? NaN)
            )
                return 'purchase_date';
            if (
                (hasHeader &&
                    (lower.includes('amount') ||
                        lower.includes('amt') ||
                        lower.includes('price') ||
                        lower.includes('cost'))) ||
                !isNaN(Number(header.replace(/[\$,]/g, '').trim()))
            )
                return 'amount';
            return '';
        });

        this.bulkPreviewRows = dataRows.map((row) => ({
            values: row.map((val) => val.trim()),
            category: null,
        }));

        this.isParsing = false;
    }

    findCategoriesFromDescriptions() {
        this.isSearchingCategories = true;
        const descriptionIndex = this.bulkFieldMapping.indexOf('description');
        const descriptionRequestData: BudgetDescriptionCategoryRequest[] =
            this.bulkPreviewRows.map((row, i) => ({
                index: i,
                description: row.values[descriptionIndex],
            }));

        this.budgetService
            .getDescriptionCategories(
                this.budgetConfiguration!.id,
                descriptionRequestData
            )
            .subscribe({
                next: (res) => {
                    this.bulkPreviewRows.forEach((row, i) => {
                        // if (row.category) return;
                        const category_id = res.find(
                            (f) => f.index === i
                        )?.category;
                        if (!category_id) return;
                        row.category = category_id;
                    });
                    this.isSearchingCategories = false;
                },
                error: (error) => {
                    this.logger.error(
                        'Error getting description categories',
                        error
                    );
                    this.toastService.show(
                        'Error getting description categories',
                        'error',
                        3000
                    );
                    this.isSearchingCategories = false;
                },
            });
    }

    removeBulkRow(index: number) {
        this.bulkPreviewRows.splice(index, 1);
    }

    parseFlexibleDate(input: string): Date | null {
        const formats = [
            {
                regex: /^(\d{4})[-\/](\d{1,2})[-\/](\d{1,2})$/,
                order: ['year', 'month', 'day'],
            }, // yyyy-mm-dd or yyyy/mm/dd
            {
                regex: /^(\d{1,2})[\/-](\d{1,2})[\/-](\d{4})$/,
                order: ['day', 'month', 'year'],
            }, // dd/mm/yyyy or dd-mm-yyyy
            {
                regex: /^(\d{1,2})[\/-](\d{1,2})[\/-](\d{2})$/,
                order: ['day', 'month', 'yearShort'],
            }, // dd/mm/yy or dd-mm-yy
            {
                regex: /^(\d{1,2})[ -](\w{3})[ -](\d{2})$/,
                order: ['day', 'monthShort', 'yearShort'],
            }, // dd MMM yy
            {
                regex: /^(\d{1,2})[ -](\w{3})[ -](\d{4})$/,
                order: ['day', 'monthShort', 'year'],
            }, // dd MMM yyyy
            {
                regex: /^(\w{3})[ -](\d{1,2})[ -](\d{2})$/,
                order: ['monthShort', 'day', 'yearShort'],
            }, // MMM dd yy
            {
                regex: /^(\w{3})[ -](\d{1,2})[ -](\d{4})$/,
                order: ['monthShort', 'day', 'year'],
            }, // MMM dd yyyy}
        ];

        const monthShorts = [
            'jan',
            'feb',
            'mar',
            'apr',
            'may',
            'jun',
            'jul',
            'aug',
            'sep',
            'oct',
            'nov',
            'dec',
        ];

        for (const fmt of formats) {
            const match = input.trim().toLowerCase().match(fmt.regex);
            if (!match) continue;

            const parts: Record<string, number> = {};
            fmt.order.forEach((part, i) => {
                let valRaw = match[i + 1].trim();
                let val: number;

                if (part === 'monthShort') {
                    const idx = monthShorts.indexOf(
                        valRaw.toLowerCase().slice(0, 3)
                    );
                    if (idx === -1) return; // invalid month
                    parts['month'] = idx + 1;
                } else if (part === 'yearShort') {
                    val = parseInt(valRaw, 10);
                    parts['year'] = val < 50 ? 2000 + val : 1900 + val;
                } else if (part === 'yearAny') {
                    val = parseInt(valRaw, 10);
                    parts['year'] =
                        valRaw.length === 2
                            ? val < 50
                                ? 2000 + val
                                : 1900 + val
                            : val;
                } else {
                    parts[part] = parseInt(valRaw, 10);
                }
            });

            // JS months are 0-indexed
            const date = new Date(
                parts['year'],
                parts['month'] - 1,
                parts['day']
            );
            if (!isNaN(date.getTime())) {
                return date;
            }
        }

        return null;
    }

    saveBulkImport() {
        // Ensure required fields are mapped
        const requiredFields: (keyof BudgetPurchase)[] = [
            'purchase_date',
            'amount',
            'description',
        ];

        const fieldCounts: Record<string, number> = {};
        for (const field of this.bulkFieldMapping) {
            if (field === '') continue;
            fieldCounts[field] = (fieldCounts[field] || 0) + 1;
        }

        // Check for missing or duplicate mappings
        for (const key of requiredFields) {
            const count = fieldCounts[key] || 0;
            if (count === 0) {
                this.toastService.show(
                    `Missing mapping for ${key}`,
                    'error',
                    5000
                );
                return;
            }
            if (count > 1) {
                this.toastService.show(
                    `Field type "${key}" is mapped more than once. Each field must be unique.`,
                    'error',
                    5000
                );
                return;
            }
        }
        // Get column indexes
        const purchaseDateIndex =
            this.bulkFieldMapping.indexOf('purchase_date');
        const amountIndex = this.bulkFieldMapping.indexOf('amount');
        const descriptionIndex = this.bulkFieldMapping.indexOf('description');

        if (
            purchaseDateIndex === -1 ||
            amountIndex === -1 ||
            descriptionIndex === -1
        ) {
            this.toastService.show(
                'All field types must be mapped before importing.',
                'error',
                3000
            );
            return;
        }

        const result: BudgetPurchase[] = this.bulkPreviewRows.map((row, i) => {
            // Validate dates are in the correct format
            const rawDate = row.values[purchaseDateIndex];
            const parsedDate = this.parseFlexibleDate(rawDate);

            if (!parsedDate) {
                this.toastService.show(
                    `Invalid date format in row ${i + 1}`,
                    'error',
                    3000
                );
                throw new Error('Invalid date format');
            }

            const amount = parseFloat(
                row.values[amountIndex].replace(/[\$,]/g, '') || '0'
            );

            return {
                purchase_date: parsedDate,
                amount: this.bulkInvertPrice ? -amount : amount,
                description: row.values[descriptionIndex],
                category: row.category ?? null,
            };
        });

        this.budgetService
            .addBulkPurchase(this.budgetConfiguration!.id, result)
            .subscribe({
                next: (res) => {
                    this.toastService.show(
                        `Imported ${res.length} purchases`,
                        'success',
                        3000
                    );
                    this.loadPurchases(true);
                    this.isBulkImportModalOpen = false;
                },
                error: (error) => {
                    this.toastService.show(
                        'Error importing purchases',
                        'error',
                        3000
                    );
                    this.logger.error('Error importing purchases', error);
                },
            });
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
