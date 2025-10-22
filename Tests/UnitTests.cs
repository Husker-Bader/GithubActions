namespace GithubActionsLab;

[TestClass]
public class Addition
{
	[TestMethod]
	public void Add_Valid_Patino()
	{
		Assert.AreEqual(3, Program.Add("1", "2"));
		Assert.AreEqual(5, Program.Add("3", "2"));
		Assert.AreEqual(12, Program.Add("5", "7"));
	}

	[TestMethod]
	public void Add_Invalid_Patino()
	{
		Assert.ThrowsException<FormatException>(() => Program.Add("1", "a"));
		Assert.ThrowsException<FormatException>(() => Program.Add("a", "1"));
		Assert.ThrowsException<FormatException>(() => Program.Add("a", "a"));
	}

	[TestMethod]
	public void Add_Null_Patino()
	{
		Assert.ThrowsException<ArgumentNullException>(() => Program.Add("1", null));
		Assert.ThrowsException<ArgumentNullException>(() => Program.Add(null, "1"));
		Assert.ThrowsException<ArgumentNullException>(() => Program.Add(null, null));
	}

	// --- NEW TESTS BELOW ---

	[TestMethod]
	public void Subtract_Valid_Patino()
	{
		Assert.AreEqual(1, Program.Subtract("3", "2"));
	}

	[TestMethod]
	public void Multiply_Valid_Patino()
	{
		Assert.AreEqual(6, Program.Multiply("3", "2"));
	}

	[TestMethod]
	public void Divide_Valid_Patino()
	{
		Assert.AreEqual(2, Program.Divide("4", "2"));
	}

	[TestMethod]
	public void Power_Valid_Patino()
	{
		Assert.AreEqual(8, Program.Power("2", "3"));
	}
}
