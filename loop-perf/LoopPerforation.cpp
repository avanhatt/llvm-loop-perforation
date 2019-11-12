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
#include "json.hpp"
#include <fstream>
#include <sstream>

using namespace llvm;
using namespace nlohmann;
using namespace std;

namespace {
  int fileexists(string filename){
    /* try to open file to read */
    FILE *file;
    if ((file = fopen(filename.c_str(), "r"))) {
        fclose(file);
        return 1;
    }
    return 0;
  }

  // -info is a command line argument to opt
  static cl::opt<string> InfoFilename(
    "info", // Name of command line arg
    cl::desc("Specify the filename to write the loop info to"), // -help text
    cl::init("loop-info.json") // Default value
  );

  // -rates is a command line argument to opt
  static cl::opt<string> RatesFilename(
    "rates", // Name of command line arg
    cl::desc("Specify the filename to read the loop rates from"), // -help text
    cl::init("loop-rates.json") // Default value
  );

  // Taken from llvm's Loop::Print()
  // But doesn't print loop depth
  std::string StringifyLoop(Loop *L) {
    std::string LoopString;
    raw_string_ostream LoopStream(LoopString);
    BasicBlock *H = L->getHeader();
    for (unsigned i = 0; i < L->getBlocks().size(); ++i) {
      BasicBlock *BB = L->getBlocks()[i];
      if (i)
        LoopStream << ",";
      BB->printAsOperand(LoopStream, false);
      if (BB == H)
        LoopStream << "<header>";
      if (L->isLoopLatch(BB))
        LoopStream << "<latch>";
      if (L->isLoopExiting(BB))
        LoopStream << "<exiting>";
    }
    return LoopStream.str();
  }

  struct LoopCountPass : public FunctionPass {
    static char ID;
    json j;
    LoopCountPass() : FunctionPass(ID) { }

    // Write one JSON file in the destructor so it is only written once
    // Expectation: one module per .ll file (but we don't rely on this)
    ~LoopCountPass() {
      std::ofstream JsonFile;
      JsonFile.open(InfoFilename);
      JsonFile << j.dump(4) << "\n";
      JsonFile.close();
    }

    void getAnalysisUsage(AnalysisUsage &AU) const {
      AU.addRequired<LoopInfoWrapperPass>();
      AU.addRequiredID(LoopSimplifyID);
    }

    // Record the loop's basic blocks in the JSON and handle subloops
    void handleLoop(Function &F, Loop *L, int &NumLoops) {
      NumLoops++;
      j[F.getParent()->getName()][F.getName()][StringifyLoop(L)] = {};
      for (Loop *SubLoop : L->getSubLoops()) {
        handleLoop(F, SubLoop, NumLoops);
      }
    }

    // Get the canonical form of all the function's loops
    virtual bool runOnFunction(Function &F) {
      LoopInfo &LI = getAnalysis<LoopInfoWrapperPass>().getLoopInfo();
      int NumLoops = 0;
      for (auto &L : LI) {
        handleLoop(F, L, NumLoops);
      }
      return false;
    }
  };



  struct LoopPerforationPass : public LoopPass {
    static char ID;
    json j;

    // Read the JSON with each loop's perforation rate
    LoopPerforationPass() : LoopPass(ID) {
      std::ifstream JsonFile;
      std::stringstream buffer;

      if (fileexists(RatesFilename)) {
        JsonFile.open(RatesFilename);
        buffer << JsonFile.rdbuf();
        JsonFile.close();
        j = json::parse(buffer.str());
      }
    }

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

          int LoopRate = 1;
          if (!j.empty()) {
            LoopRate = j[F->getParent()->getName()][F->getName()][StringifyLoop(L)];
          }
          Type *ConstType = Op->getType();
          Constant *NewInc = ConstantInt::get(ConstType, LoopRate /*value*/, true /*issigned*/);

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
char LoopCountPass::ID = 1;

// Register the pass so `opt -loop-perf` runs it.
static RegisterPass<LoopPerforationPass> X("loop-perf", "loop perforation pass");
static RegisterPass<LoopCountPass> Y("loop-count", "loop counting pass");
