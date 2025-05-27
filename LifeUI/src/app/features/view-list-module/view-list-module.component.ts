import { Component, ElementRef, inject, QueryList, ViewChildren } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { NgIcon, provideIcons } from '@ng-icons/core';
import {
    ionPencil,
    ionTrashBin,
    ionAdd,
} from '@ng-icons/ionicons';
import { ListConfiguration, ListItem } from '@core/models/list.model';
import { ListService } from '@core/services/list.service';
import { ReferenceService } from '@core/services/reference.service';
import { FieldType } from '@core/models/fieldType.model';
import { PaginatedResponse } from '@core/models/pagination.model';
import { FormsModule } from '@angular/forms';
import { LoggerService } from '@core/services/logger.service';
import { ModalComponent } from '@layout/modal/modal.component';

@Component({
    selector: 'app-view-list-module',
    standalone: true,
    imports: [NgIcon, RouterLink, ModalComponent, FormsModule],
    providers: [provideIcons({
        ionPencil,
        ionTrashBin,
        ionAdd,
    })],
    templateUrl: './view-list-module.component.html'
})
export class ViewListModuleComponent {
    private route = inject(ActivatedRoute);
    private router = inject(Router);
    private listService = inject(ListService);
    private referenceService = inject(ReferenceService);
    private logger = inject(LoggerService);


    moduleId = Number(this.route.snapshot.paramMap.get('id'));
    listConfiguration: ListConfiguration | null = null;
    listData: PaginatedResponse<ListItem> | null = null
    fieldTypes: FieldType[] = [];
    isLoading = true;
    currentPage = 1;
    isSetItemModalOpen = false;
    setItemForm: ListItem = {
        user_module: this.moduleId,
        is_completed: false,
        field_values: []
    };

    @ViewChildren('inputField') inputFields!: QueryList<ElementRef>;

    ngOnInit() {
        this.route.paramMap.subscribe(params => {
            this.moduleId = Number(params.get('id'));

            this.loadModule();
            this.loadListData();
        });

        this.referenceService.getFieldTypesWithRules().subscribe({
            next: (res) => {
                this.fieldTypes = res;
            },
            error: (error) => {
                this.logger.error('Error fetching field types', error);
            }
        });
    }

    private loadModule() {
        this.isLoading = true;
        this.listService.getModule(this.moduleId).subscribe({
            next: (res) => {
                this.listConfiguration = res;
                this.isLoading = false;
            },
            error: (error) => {
                this.isLoading = false;
                alert('Module not found');
                this.router.navigate(['/modules']);
            }
        });
    }

    private loadListData() {
        this.listService.getListData(this.moduleId).subscribe({
            next: (res) => {
                this.listData = res;
                this.currentPage = 1;
            },
            error: (error) => {
                this.logger.error('Error fetching list data', error);
            }
        });
    }

    loadPage(direction: 'next' | 'previous') {
        if (!this.listData) return;

        let targetUrl: string | null = null;

        if (direction === 'next') {
            targetUrl = this.listData.next;
            this.currentPage++;
        } else if (direction === 'previous') {
            targetUrl = this.listData.previous;
            this.currentPage--;
        }

        if (!targetUrl) return;

        this.listService.getListDataByUrl(targetUrl).subscribe({
            next: (res) => {
                this.listData = res;
            },
            error: (error) => {
                this.logger.error('Error fetching list data', error);
            }
        });
    }

    getListFieldValue(item: ListItem, fieldId: number): string {
        const fieldValue = item.field_values.find(fv => fv.field === fieldId);
        return fieldValue ? fieldValue.value : '';
    }

    getFormFieldValue(fieldId: number): string {
        const fieldValue = this.setItemForm.field_values.find(fv => fv.field === fieldId);
        return fieldValue ? fieldValue.value : '';
    }

    setFormFieldValue(fieldId: number, value: string): void {
        const fieldValue = this.setItemForm.field_values.find(fv => fv.field === fieldId);
        if (fieldValue) {
            fieldValue.value = value;
        } else {
            this.setItemForm.field_values.push({ field: fieldId, value });
        }
    }

    toggleCompleted(item: ListItem): void {
        this.listService.updateListItemCompletion(this.moduleId, item.id!, !item.is_completed).subscribe({
            next: () => {
                item.is_completed = !item.is_completed;
            },
            error: (error) => {
                this.logger.error('Error updating item', error);
            }
        });
    }

    confirmDeleteItem(itemId: number): void {
        if (confirm('Are you sure you want to delete this item?')) {
            this.deleteItem(itemId);
        }
    }

    deleteItem(itemId: number): void {
        this.listService.deleteListItem(this.moduleId, itemId).subscribe({
            next: () => {
                this.deleteItemLocally(itemId);
            },
            error: (error) => {
                this.logger.error('Error deleting item', error);
            }
        });
    }

    deleteItemLocally(itemId: number) {
        if (!this.listData?.results) return;

        const index = this.listData.results.findIndex(item => item.id === itemId);
        if (index !== -1) {
            this.listData.results.splice(index, 1);
            this.listData.count -= 1;
        }

        if (this.listData.results.length === 0 && this.currentPage > 1) {
            this.loadPage('previous');
        }
        else if (this.listData.next) {
            this.reloadCurrentPage();
        }
    }

    reloadCurrentPage() {
        this.isLoading = true;

        this.listService.getListDataByPage(this.moduleId, this.currentPage).subscribe({
            next: (res) => {
                this.listData = res;
                this.isLoading = false;
            },
            error: (error) => {
                this.logger.error('Error fetching list data', error);
                this.isLoading = false;
            }
        });
    }

    get sortedFields() {
        return this.listConfiguration?.list_fields.sort((a, b) => a.order - b.order) ?? [];
    }

    openSetItemModal(item?: ListItem) {
        this.isSetItemModalOpen = true;

        this.setItemForm = {
            user_module: this.moduleId,
            is_completed: false,
            field_values: []
        };

        if (item) {
            this.setItemForm = structuredClone(item);
        }

        setTimeout(() => {
            const firstInput = this.inputFields?.first;
            if (firstInput) {
                firstInput.nativeElement.focus();
            }
        });
    }

    closeSetItemModal() {
        this.isSetItemModalOpen = false;
    }

    saveSetItem() {
        if (this.setItemForm?.id) {
            // Update existing
            this.listService.updateListItem(this.moduleId, this.setItemForm).subscribe({
                next: (res) => {
                    this.isSetItemModalOpen = false;
                    this.updateItemLocally(res);
                },
                error: (error) => {
                    this.logger.error('Error updating item', error);
                }
            });
        } else {
            // Add new
            this.listService.addListItem(this.moduleId, this.setItemForm!).subscribe({
                next: (res) => {
                    this.isSetItemModalOpen = false;
                    this.addItemLocally(res);
                },
                error: (error) => {
                    this.logger.error('Error adding item', error);
                }
            });
        }
    }

    addItemLocally(newItem: ListItem) {
        if (!this.listData?.results) return;

        this.listData.results.unshift(newItem);

        if (this.listData.results.length > 10) {
            this.listData.results.pop();
        }

        this.listData.count += 1;
    }

    updateItemLocally(updatedItem: ListItem) {
        if (!this.listData?.results) return;

        const index = this.listData.results.findIndex(item => item.id === updatedItem.id);
        if (index !== -1) {
            this.listData.results[index] = updatedItem;
        }
    }

}
