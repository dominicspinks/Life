import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BudgetSummaryTabComponent } from './budget-summary-tab.component';

describe('BudgetSummaryTabComponent', () => {
  let component: BudgetSummaryTabComponent;
  let fixture: ComponentFixture<BudgetSummaryTabComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [BudgetSummaryTabComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(BudgetSummaryTabComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
