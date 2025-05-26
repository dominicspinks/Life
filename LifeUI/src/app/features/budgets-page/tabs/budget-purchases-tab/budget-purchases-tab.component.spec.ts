import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BudgetPurchasesTabComponent } from './budget-purchases-tab.component';

describe('BudgetPurchasesTabComponent', () => {
  let component: BudgetPurchasesTabComponent;
  let fixture: ComponentFixture<BudgetPurchasesTabComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [BudgetPurchasesTabComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(BudgetPurchasesTabComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
