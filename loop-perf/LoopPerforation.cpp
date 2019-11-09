#include "llvm/Analysis/LoopInfo.h"
#include "llvm/Analysis/LoopPass.h"
#include "llvm/Analysis/IVUsers.h"
#include "llvm/Pass.h"
#include "llvm/IR/Function.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/IR/LegacyPassManager.h"
#include "llvm/Transforms/IPO/PassManagerBuilder.h"
#include "llvm/Transforms/Utils.h"
#include "llvm/Transforms/Utils/Mem2Reg.h"
#include "llvm/Support/CommandLine.h"
using namespace llvm;

namespace {

  // rate is a command line argument to opt
  static cl::opt<unsigned> Rate(
    "rate", // Name of command line arg
    cl::desc("Increase the induction variable by this amount every iteration"), // -help text
    cl::init(2) // Default value
  );

  template <typename T>
  bool contains(std::list<T> & l, const T & element)
  {
    auto it = std::find(l.begin(), l.end(), element);
    return it != l.end();
  }

  struct LoopPerforationPass : public LoopPass {
    static char ID;
    LoopPerforationPass() : LoopPass(ID) {}

    void getAnalysisUsage(AnalysisUsage &AU) const {
      AU.addRequired<LoopInfoWrapperPass>();
      AU.addRequired<IVUsersWrapperPass>();
      AU.addRequiredID(LoopSimplifyID);
    }

    virtual bool runOnLoop(Loop *L, LPPassManager &LPM) {

      // Don't perforate loops in main for testability
      const Function *F = L->getHeader()->getParent();
      if (F->getName() == "main") {
        return false;
      }

      // We don't modify unsimplified loops
      bool IsSimple = L->isLoopSimplifyForm();
      if (!IsSimple) {
        errs() << "Loop is not simple, skipping" << *L << "\n";
        return false;
      }

      // Find the canonical induction variable for this loop
      PHINode *PHI = L->getCanonicalInductionVariable();

      if (PHI == nullptr) {
        errs() << "No induction variable! :( \n";
        return false;
      }

      errs() << "Induction variable:  " << *PHI << "!\n";

      // Find where the induction variable is modified by finding a user that
      // is also an incoming value to the phi
      Value *ValueToChange = nullptr;

      for (auto User : PHI->users()) {
        for (auto &Incoming : PHI->incoming_values()) {
          if (Incoming == User) {
            errs() << "Found the value to change!" << *User << "!\n";
            ValueToChange = Incoming;
            break; // TODO: what if there are multiple?
          }
        }
      }

      if (ValueToChange == nullptr) {
        errs() << "No value to change! :( \n";
        return false;
      }

      if (isa<BinaryOperator>(ValueToChange)) {
        BinaryOperator *Increment = dyn_cast<BinaryOperator>(ValueToChange);

        for (auto &Op : Increment->operands()) {
          if (Op == PHI) continue;

          // Hardcode:
          Type *ConstType = Op->getType();
          Constant *NewInc = ConstantInt::get(ConstType, Rate /*value*/, true /*issigned*/);

          errs() << "Changing [" << *Op << "] to [" << *NewInc << "]!\n";

          Op = NewInc;
          return true;
        }
      }

      return false;
    }
  };
}

char LoopPerforationPass::ID = 0;

// Register the pass so `opt -loop-perf` runs it.
static RegisterPass<LoopPerforationPass> X("loop-perf", "loop perforation pass");
